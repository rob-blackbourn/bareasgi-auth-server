# Demos

This folder contains some example programs.

For the examples to work a remote proxy must be configured
to present the URLs as part of a single domain.

For example, if the host was `example.com`:

- example_auth_server serves on http://localhost:10001/auth/api which should be mapped to https://example.com/auth/api
- example-auth-ui serves on http://localhost:10002/auth/ui which should be mapped to https://example.com/auth/ui
- example_api_server serves on http://localhost:10010/example/api which should be mapped to https://example.com/example/api
- example-test-ui serves on http://localhost:10011/example/ui which should be mapped to https://example.com/example/ui
