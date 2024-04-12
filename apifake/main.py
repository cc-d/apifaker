import json
import random
from typing import Any, Dict, Type

from fastapi import FastAPI, Response, status
from pydantic import BaseModel, create_model
from pyshared import List, Opt, U, default_repr


class ApiSpec:
    spec: dict

    def __init__(self, spec_or_path: U[str, dict]):
        if isinstance(spec_or_path, str):
            with open(spec_or_path, 'r') as file:
                self.spec = json.load(file)
        else:
            self.spec = spec_or_path

    def __repr__(self):
        return default_repr(self)


class ApiRoute:
    """Represents a single API route in an OpenAPI specification."""

    def __init__(self, path: str, method: str, details: Dict[str, Any]):
        self.path = path
        self.method = method
        self.details = details
        self.response_model = self.create_response_model()

    def get_response_schema(self) -> Dict[str, Any]:
        """Extract the response schema for successful HTTP responses."""
        responses = self.details.get('responses', {})
        success_code = str(
            min(
                (
                    int(code)
                    for code in responses.keys()
                    if code.startswith('2')
                ),
                default=200,
            )
        )
        return (
            responses.get(success_code, {})
            .get('content', {})
            .get('application/json', {})
            .get('schema', {})
        )

    def create_response_model(self) -> Type[BaseModel]:
        """Create a Pydantic model from the response schema."""
        schema = self.get_response_schema()
        properties = {}
        required = schema.get('required', [])
        for prop_name, prop_info in schema.get('properties', {}).items():
            prop_type = self.get_type(prop_info)
            default = ... if prop_name in required else None
            properties[prop_name] = (prop_type, default)
        return create_model(
            f"{self.path.replace('/', '_')}_{self.method}_ResponseModel",
            **properties,
        )

    def get_type(self, schema: Dict[str, Any]) -> Any:
        """Map JSON schema types to Python types used by Pydantic."""
        schema_type = schema.get('type', 'string')
        if schema_type == 'string':
            return str
        elif schema_type == 'number':
            return float
        elif schema_type == 'integer':
            return int
        elif schema_type == 'boolean':
            return bool
        elif schema_type == 'array':
            item_type = self.get_type(schema.get('items', {}))
            return List[item_type]  # This uses typing.List
        elif schema_type == 'object':
            # More complex handling might be needed for nested objects
            return dict
        return Any

    def generate_mock_data(self) -> Any:
        """Generate mock data based on the response model."""
        return self.response_model().dict()

    def __repr__(self):
        return default_repr(self)


class ApiFake:
    app: FastAPI

    def __init__(self, spec: ApiSpec):
        self.app = FastAPI()
        self.spec = spec
        for path, methods in self.spec.get('paths', {}).items():
            for method, details in methods.items():
                route = ApiRoute(path, method, details)
                self.add_route(route)

    def add_route(self, route: ApiRoute):
        """Add a single route to the FastAPI application."""
        endpoint_path = route.path.replace('{', '{{').replace('}', '}}')

        async def endpoint(**kwargs):
            """Endpoint function that generates mock responses based on the route's response schema."""
            mock_data = route.generate_mock_data()
            return Response(
                content=json.dumps(mock_data), media_type="application/json"
            )

        self.app.add_api_route(
            endpoint_path, endpoint, methods=[route.method.upper()]
        )

    def __repr__(self):
        return default_repr(self)

    def start(self, host: str = "fakeapi", port: int = 8000):
        """Start the FastAPI application."""
        yield self.app.run_server(host=host, port=port)

    def routes(self):
        """Return a list of all routes in the FastAPI application."""
        return [route for route in self.app.routes]
