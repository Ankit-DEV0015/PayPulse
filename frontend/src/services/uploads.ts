
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000/api/v1";

export interface UploadPreview {
  filename: string;
  file_type: string;
  row_count: number;
  columns: string[];
  preview: Record<string, unknown>[];
  message: string;
}

export async function uploadTransactionFile(
  file: File
): Promise<UploadPreview> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    `${API_BASE_URL}/uploads/preview`,
    formData,
    {
      withCredentials: true,
      timeout: 60000,
    }
  );

  const data = response.data;

  // Current FastAPI endpoint returns preview as a JSON string.
  // Support both string and array formats.
  const preview =
    typeof data.preview === "string"
      ? JSON.parse(data.preview)
      : data.preview;

  return {
    ...data,
    preview,
  };
}
