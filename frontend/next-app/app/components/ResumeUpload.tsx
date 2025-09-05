"use client";

import { useState } from "react";
import axios from "axios";

export default function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
    }
  };

  const uploadResume = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `${
          process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
        }/upload-resume`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setResult(response.data);
    } catch (error) {
      console.error("Error uploading resume:", error);
      setResult({ error: "Error uploading resume. Please try again." });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Upload Resume</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Resume File (PDF or DOCX)
          </label>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        {file && (
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm text-gray-700">
              Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </span>
            <button
              onClick={uploadResume}
              disabled={uploading}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? "Uploading..." : "Upload & Parse"}
            </button>
          </div>
        )}

        {result && (
          <div className="mt-4">
            {result.error ? (
              <div className="p-3 bg-red-100 text-red-700 rounded-lg">
                {result.error}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-green-100 text-green-700 rounded-lg">
                  Resume uploaded successfully!
                </div>

                {result.parsed_data && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold mb-2">
                      Extracted Information:
                    </h3>
                    <div className="space-y-2 text-sm">
                      {result.parsed_data.extracted_info.name && (
                        <p>
                          <strong>Name:</strong>{" "}
                          {result.parsed_data.extracted_info.name}
                        </p>
                      )}
                      {result.parsed_data.extracted_info.email && (
                        <p>
                          <strong>Email:</strong>{" "}
                          {result.parsed_data.extracted_info.email}
                        </p>
                      )}
                      {result.parsed_data.extracted_info.phone && (
                        <p>
                          <strong>Phone:</strong>{" "}
                          {result.parsed_data.extracted_info.phone}
                        </p>
                      )}
                      {result.parsed_data.extracted_info.skills &&
                        result.parsed_data.extracted_info.skills.length > 0 && (
                          <p>
                            <strong>Skills:</strong>{" "}
                            {result.parsed_data.extracted_info.skills.join(
                              ", "
                            )}
                          </p>
                        )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div className="p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">📋 How it works:</h3>
          <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
            <li>Upload your resume (PDF or DOCX format)</li>
            <li>The system extracts and structures your information</li>
            <li>Your resume context is loaded for AI chat</li>
            <li>Start chatting about your CV in the Chat tab!</li>
          </ol>
        </div>

        <div className="p-4 bg-yellow-50 rounded-lg">
          <h3 className="font-medium text-yellow-900 mb-2">🔒 Privacy Note:</h3>
          <p className="text-sm text-yellow-800">
            Your resume is processed locally and not permanently stored. The
            extracted information is used only for AI chat functionality.
          </p>
        </div>
      </div>
    </div>
  );
}
