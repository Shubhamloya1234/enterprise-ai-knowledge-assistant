import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/auth";

function Documents() {
    const { user } = useAuth();

    const [documents, setDocuments] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [deleting, setDeleting] = useState(null);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const isAdmin = user?.role === "ADMIN";

    const loadDocuments = useCallback(async () => {
        setError("");

        try {
            const response = await api.get("/documents/");

            setDocuments(response.data.documents || []);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to load documents."
            );
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            loadDocuments();
        }, 0);

        return () => clearTimeout(timeoutId);
    }, [loadDocuments]);

    const handleFileChange = (event) => {
        setError("");
        setSuccess("");

        const file = event.target.files?.[0];

        if (!file) {
            setSelectedFile(null);
            return;
        }

        const extension = file.name
            .slice(file.name.lastIndexOf("."))
            .toLowerCase();

        if (![".pdf", ".txt"].includes(extension)) {
            setError("Only PDF and TXT files are supported.");
            event.target.value = "";
            setSelectedFile(null);
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            setError("Maximum file size is 10 MB.");
            event.target.value = "";
            setSelectedFile(null);
            return;
        }

        setSelectedFile(file);
    };

    const handleUpload = async (event) => {
        event.preventDefault();

        if (!selectedFile || uploading) {
            return;
        }

        setUploading(true);
        setError("");
        setSuccess("");

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await api.post(
                "/documents/upload",
                formData
            );

            setSuccess(
                `${response.data.filename} uploaded successfully. ` +
                `${response.data.chunks} chunks indexed.`
            );

            setSelectedFile(null);
            event.target.reset();

            await loadDocuments();
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Document upload failed."
            );
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (filename) => {
        const confirmed = window.confirm(
            `Delete "${filename}" permanently?`
        );

        if (!confirmed) {
            return;
        }

        setDeleting(filename);
        setError("");
        setSuccess("");

        try {
            const response = await api.delete(
                `/documents/${encodeURIComponent(filename)}`
            );

            setSuccess(
                `${response.data.filename} deleted successfully.`
            );

            await loadDocuments();
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Document deletion failed."
            );
        } finally {
            setDeleting(null);
        }
    };

    if (!isAdmin) {
        return (
            <main className="documents-page">
                <h2>Access denied</h2>
                <p>Only administrators can manage documents.</p>
                <Link to="/">Return to chat</Link>
            </main>
        );
    }

    return (
        <main className="documents-page">
            <header className="documents-header">
                <div>
                    <h1>Document Management</h1>
                    <p>
                        Upload and manage documents used by the
                        enterprise knowledge assistant.
                    </p>
                </div>

                <Link className="documents-back-link" to="/">
                    Back to Chat
                </Link>
            </header>

            {error && (
                <div className="document-alert document-error">
                    {error}
                </div>
            )}

            {success && (
                <div className="document-alert document-success">
                    {success}
                </div>
            )}

            <section className="document-panel">
                <h2>Upload a document</h2>

                <p>
                    Supported formats: PDF and TXT.
                    Maximum size: 10 MB.
                </p>

                <form onSubmit={handleUpload}>
                    <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={handleFileChange}
                        disabled={uploading}
                    />

                    {selectedFile && (
                        <p className="selected-file">
                            Selected: {selectedFile.name}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={!selectedFile || uploading}
                    >
                        {uploading
                            ? "Uploading and indexing..."
                            : "Upload Document"}
                    </button>
                </form>
            </section>

            <section className="document-panel">
                <div className="document-list-header">
                    <div>
                        <h2>Uploaded documents</h2>
                        <p>
                            {documents.length} document(s)
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={loadDocuments}
                        disabled={loading}
                    >
                        Refresh
                    </button>
                </div>

                {loading ? (
                    <p>Loading documents...</p>
                ) : documents.length === 0 ? (
                    <p>No documents uploaded yet.</p>
                ) : (
                    <div className="document-list">
                        {documents.map((filename) => (
                            <div
                                className="document-item"
                                key={filename}
                            >
                                <div className="document-name">
                                    <span className="document-icon">
                                        {filename.toLowerCase().endsWith(".pdf")
                                            ? "PDF"
                                            : "TXT"}
                                    </span>

                                    <span>{filename}</span>
                                </div>

                                <button
                                    type="button"
                                    className="document-delete-button"
                                    disabled={deleting !== null}
                                    onClick={() => handleDelete(filename)}
                                >
                                    {deleting === filename
                                        ? "Deleting..."
                                        : "Delete"}
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </main>
    );
}

export default Documents;