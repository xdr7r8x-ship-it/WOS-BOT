import os
import pytest
import subprocess


class TestFrontendBuild:
    def test_frontend_directory_exists(self):
        assert os.path.exists("src/web/frontend")

    def test_package_json_exists(self):
        assert os.path.exists("src/web/frontend/package.json")

    def test_vite_config_exists(self):
        assert os.path.exists("src/web/frontend/vite.config.ts")

    def test_typescript_config_exists(self):
        assert os.path.exists("src/web/frontend/tsconfig.json")

    def test_index_html_exists(self):
        assert os.path.exists("src/web/frontend/index.html")

    def test_src_directory_exists(self):
        assert os.path.exists("src/web/frontend/src")

    def test_pages_directory_has_files(self):
        pages_dir = "src/web/frontend/src/pages"
        if os.path.exists(pages_dir):
            files = os.listdir(pages_dir)
            assert len(files) > 0, "Pages directory should have files"
        else:
            pytest.skip("Pages directory not found")


class TestFrontendComponents:
    def test_api_client_exists(self):
        assert os.path.exists("src/web/frontend/src/api/client.ts")

    def test_auth_provider_exists(self):
        assert os.path.exists("src/web/frontend/src/auth/AuthProvider.tsx")

    def test_layout_exists(self):
        assert os.path.exists("src/web/frontend/src/layout/DashboardLayout.tsx")

    def test_app_tsx_exists(self):
        assert os.path.exists("src/web/frontend/src/App.tsx")

    def test_i18n_files_exist(self):
        assert os.path.exists("src/web/frontend/src/i18n/ar.json")
        assert os.path.exists("src/web/frontend/src/i18n/en.json")
