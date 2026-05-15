from pathlib import Path

from httpx import AsyncClient


class TestHealth:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestUploadDocument:
    async def test_upload_pdf(self, client: AsyncClient, tmp_path: Path):
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        resp = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", pdf.read_bytes(), "application/pdf")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "document_id" in data
        assert data["filename"] == "test.pdf"

    async def test_upload_png(self, client: AsyncClient, tmp_path: Path):
        png = tmp_path / "test.png"
        png.write_bytes(b"\x89PNG fake png content")

        resp = await client.post(
            "/api/documents/upload",
            files={"file": ("test.png", png.read_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "document_id" in data

    async def test_upload_rejected_type(self, client: AsyncClient, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_bytes(b"plain text")

        resp = await client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", txt.read_bytes(), "text/plain")},
        )
        assert resp.status_code == 400

    async def test_upload_no_file(self, client: AsyncClient):
        resp = await client.post("/api/documents/upload")
        assert resp.status_code == 422


class TestGenerateReview:
    async def test_generate_review(self, client: AsyncClient, tmp_path: Path):
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 content")
        upload = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", pdf.read_bytes(), "application/pdf")},
        )
        doc_id = upload.json()["document_id"]

        resp = await client.post(f"/api/documents/{doc_id}/generate")
        assert resp.status_code == 200
        data = resp.json()
        assert "review" in data
        assert data["review"].startswith("# Title Review")

    async def test_generate_missing_doc(self, client: AsyncClient):
        resp = await client.post("/api/documents/bogus-id/generate")
        assert resp.status_code == 404


class TestGetReview:
    async def test_get_review_empty(self, client: AsyncClient, tmp_path: Path):
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 content")
        upload = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", pdf.read_bytes(), "application/pdf")},
        )
        doc_id = upload.json()["document_id"]

        resp = await client.get(f"/api/documents/{doc_id}/review")
        assert resp.status_code == 200
        assert resp.json() == {"content": ""}

    async def test_get_review_after_generate(self, client: AsyncClient, tmp_path: Path):
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 content")
        upload = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", pdf.read_bytes(), "application/pdf")},
        )
        doc_id = upload.json()["document_id"]
        await client.post(f"/api/documents/{doc_id}/generate")

        resp = await client.get(f"/api/documents/{doc_id}/review")
        assert resp.status_code == 200
        assert "review" not in resp.json()
        assert "content" in resp.json()

    async def test_get_review_missing_doc(self, client: AsyncClient):
        resp = await client.get("/api/documents/bogus-id/review")
        assert resp.status_code == 404


class TestSaveReview:
    async def test_save_review(self, client: AsyncClient, tmp_path: Path):
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 content")
        upload = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", pdf.read_bytes(), "application/pdf")},
        )
        doc_id = upload.json()["document_id"]

        resp = await client.put(
            f"/api/documents/{doc_id}/review",
            json={"content": "# Edited Review\n\nUpdated content."},
        )
        assert resp.status_code == 200
        assert resp.json() == {"status": "saved"}

        get_resp = await client.get(f"/api/documents/{doc_id}/review")
        assert get_resp.json()["content"] == "# Edited Review\n\nUpdated content."

    async def test_save_review_missing_doc(self, client: AsyncClient):
        resp = await client.put(
            "/api/documents/bogus-id/review",
            json={"content": "# Test"},
        )
        assert resp.status_code == 404


class TestChat:
    async def test_send_message(self, client: AsyncClient):
        resp = await client.post("/api/chat", json={"message": "Hello"})
        assert resp.status_code == 201
        data = resp.json()
        assert "response" in data
        assert len(data["response"]) > 0

    async def test_send_empty_message(self, client: AsyncClient):
        resp = await client.post("/api/chat", json={"message": ""})
        assert resp.status_code == 422

    async def test_chat_history(self, client: AsyncClient):
        await client.post("/api/chat", json={"message": "First message"})
        await client.post("/api/chat", json={"message": "Second message"})

        resp = await client.get("/api/chat/history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["messages"]) == 4
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][0]["content"] == "First message"
        assert data["messages"][1]["role"] == "assistant"

    async def test_chat_history_empty(self, client: AsyncClient):
        resp = await client.get("/api/chat/history")
        assert resp.status_code == 200
        assert resp.json() == {"messages": []}
