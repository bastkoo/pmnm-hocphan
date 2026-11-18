"""Kiểm tra tích hợp trên bản sao tạm, không sửa dữ liệu bài tập."""

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from werkzeug.test import Client
from werkzeug.wrappers import Response


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name) / "TongHop"
        shutil.copytree(Path(__file__).parent, root,
                        ignore=shutil.ignore_patterns(".venv", "__pycache__", "test_app.py"))
        spec = importlib.util.spec_from_file_location("integration_portal", root / "app.py")
        cls.portal = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.portal
        spec.loader.exec_module(cls.portal)
        for child in cls.portal.mounted_apps.values():
            child.config["TESTING"] = True
        cls.client = Client(cls.portal.app, Response)

    @classmethod
    def tearDownClass(cls):
        for child in cls.portal.mounted_apps.values():
            if "sqlalchemy" in child.extensions:
                with child.app_context():
                    child.extensions["sqlalchemy"].session.remove()
                    child.extensions["sqlalchemy"].engine.dispose()
        cls.temp.cleanup()

    def test_pages_and_navbar(self):
        paths = ["/", "/chuong3/", "/chuong3/index", "/chuong3/about",
                 "/chuong3/thu-vien/", "/chuong3/thu-vien/books",
                 "/chuong3/thu-vien/books/1", "/chuong_03/",
                 "/chuong_03/students", "/chuong_03/students/23T1020001",
                 "/chuong_03/search?q=An", "/chuong4/", "/chuong4/menu",
                 "/chuong4/menu?page=2", "/chuong4/contact", "/chuong5/",
                 "/chuong5/bai1", "/chuong5/bai2", "/chuong5/bai3",
                 "/chuong6/", "/chuong6/ds-sinh-vien", "/bai-kiem-tra/",
                 "/bai-kiem-tra/books", "/bai-kiem-tra/categories"]
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text.count('id="course-nav"'), 1)
                for section in self.portal.SECTIONS:
                    self.assertIn('href="' + section["prefix"] + '/"', response.text)

    def test_navigation_and_static(self):
        cafe = self.client.get("/chuong4/").text
        self.assertIn('href="/chuong4/menu"', cafe)
        self.assertIn('href="/chuong4/contact"', cafe)
        self.assertIn('href="/chuong5/bai2"', self.client.get("/chuong5/").text)
        self.assertIn('/bai-kiem-tra/static/css/style.css', self.client.get('/bai-kiem-tra/').text)
        for path in ["/bai-kiem-tra/static/css/style.css", "/bai-kiem-tra/static/js/app.js"]:
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)
                self.assertNotIn('id="course-nav"', response.text)

    def test_forms(self):
        response = self.client.post("/chuong5/bai1", data={"num_a": "8", "num_b": "2", "op": "+"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("10", response.text)
        response = self.client.post("/chuong5/bai1", data={"num_a": "8", "num_b": "0", "op": "/"})
        self.assertIn("Không thể chia cho 0", response.text)
        response = self.client.post("/chuong5/bai2", data={"cc": "9", "gk": "8", "ck": "7"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("7,5", response.text)
        response = self.client.post("/chuong5/bai3", data={"chieu_cao": "170", "can_nang": "65"})
        self.assertEqual(response.status_code, 200)

    def test_api_csv_and_redirect(self):
        response = self.client.get("/chuong_03/api/students")
        self.assertEqual(len(response.json), 6)
        self.assertNotIn('id="course-nav"', response.text)
        response = self.client.get("/chuong3/thu-vien/api/books")
        self.assertEqual(len(response.json), 5)
        response = self.client.get("/chuong_03/students/23T1020001/export")
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn("hoc_phan,diem", response.text)
        self.assertNotIn('id="course-nav"', response.text)
        response = self.client.get("/chuong_03/sv/23T1020001")
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response.location.endswith("/chuong_03/students/23T1020001"))
        path = "/chuong_03/api/students/23T1020001/scores/TEST"
        self.assertEqual(self.client.put(path + "?score=8").status_code, 201)
        self.assertEqual(self.client.get(path).json["score"], 8)
        self.assertEqual(self.client.delete(path).status_code, 204)

    def test_library_crud(self):
        child = self.portal.mounted_apps["/bai-kiem-tra"]
        module = sys.modules[child.import_name]
        response = self.client.post("/bai-kiem-tra/categories/save", data={"name": "Integration Test"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/bai-kiem-tra/categories"))
        with child.app_context():
            category_id = module.Category.query.filter_by(name="Integration Test").one().id
        response = self.client.post("/bai-kiem-tra/books/save", data={
            "title": "Integration Book", "author": "Test", "category_id": category_id,
            "price": "10000", "quantity": "2"})
        self.assertEqual(response.status_code, 302)
        with child.app_context():
            book_id = module.Book.query.filter_by(title="Integration Book").one().id
        response = self.client.get(f"/bai-kiem-tra/books/{book_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Integration Book", response.text)
        self.client.post(f"/bai-kiem-tra/books/{book_id}/delete")
        self.client.post(f"/bai-kiem-tra/categories/{category_id}/delete")
        self.assertEqual(self.client.get(f"/bai-kiem-tra/books/{book_id}").status_code, 404)

    def test_databases_are_separate(self):
        for prefix, folder in [("/chuong6", "Chuong6"), ("/bai-kiem-tra", "BaiKiemTra")]:
            child = self.portal.mounted_apps[prefix]
            with child.app_context():
                database = Path(child.extensions["sqlalchemy"].engine.url.database)
                self.assertTrue(database.is_relative_to(Path(self.temp.name)))
                self.assertIn(folder, database.parts)
        self.assertEqual(self.client.get("/chuong6/them-mau").status_code, 200)
        self.assertEqual(self.client.get("/chuong6/thu-truy-van").status_code, 200)

    def test_errors(self):
        for path in ["/missing", "/chuong4/menu?page=999", "/chuong_03/students/missing"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 404)
            self.assertIn('id="course-nav"', response.text)
        response = self.client.get("/chuong_03/api/students/missing")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.is_json)


if __name__ == "__main__":
    unittest.main(verbosity=2)
