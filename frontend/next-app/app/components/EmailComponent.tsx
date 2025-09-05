"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";

interface EmailForm {
  recipient: string;
  subject: string;
  body: string;
}

export default function EmailComponent() {
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EmailForm>();

  const onSubmit = async (data: EmailForm) => {
    setSending(true);
    setResult(null);

    try {
      const response = await axios.post(
        `${
          process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
        }/send-email`,
        data
      );
      setResult("Email sent successfully!");
      reset();
    } catch (error) {
      console.error("Error sending email:", error);
      setResult("Error sending email. Please try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Send Email Notification</h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label
            htmlFor="recipient"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Recipient Email *
          </label>
          <input
            {...register("recipient", {
              required: "Email is required",
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: "Invalid email address",
              },
            })}
            type="email"
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="recipient@example.com"
          />
          {errors.recipient && (
            <p className="text-red-500 text-sm mt-1">
              {errors.recipient.message}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="subject"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Subject *
          </label>
          <input
            {...register("subject", { required: "Subject is required" })}
            type="text"
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Email subject"
          />
          {errors.subject && (
            <p className="text-red-500 text-sm mt-1">
              {errors.subject.message}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="body"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Message *
          </label>
          <textarea
            {...register("body", { required: "Message is required" })}
            rows={6}
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Your email message..."
          />
          {errors.body && (
            <p className="text-red-500 text-sm mt-1">{errors.body.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={sending}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {sending ? "Sending..." : "Send Email"}
        </button>
      </form>

      {result && (
        <div
          className={`mt-4 p-3 rounded-lg ${
            result.includes("Error")
              ? "bg-red-100 text-red-700"
              : "bg-green-100 text-green-700"
          }`}
        >
          {result}
        </div>
      )}

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-2">Quick Templates:</h3>
        <div className="space-y-2 text-sm">
          <p>
            <strong>Interview Thank You:</strong> "Thank you for the interview
            opportunity..."
          </p>
          <p>
            <strong>Follow Up:</strong> "Following up on our conversation
            about..."
          </p>
          <p>
            <strong>Introduction:</strong> "I'm reaching out to introduce
            myself..."
          </p>
        </div>
      </div>
    </div>
  );
}
