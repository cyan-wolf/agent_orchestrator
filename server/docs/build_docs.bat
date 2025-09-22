REM Build the docs for the sub-modules.
uv run sphinx-apidoc -o docs/ai_module_docs --implicit-namespaces ai
uv run sphinx-apidoc -o docs/auth_module_docs --implicit-namespaces auth
uv run sphinx-apidoc -o docs/chat_module_docs --implicit-namespaces chat
uv run sphinx-apidoc -o docs/database_module_docs --implicit-namespaces database
uv run sphinx-apidoc -o docs/user_settings_module_docs --implicit-namespaces user_settings

REM Build the documentation.
uv run sphinx-build -M html docs docs/_build/html