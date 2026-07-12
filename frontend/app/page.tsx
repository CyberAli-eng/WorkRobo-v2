"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function HomePage() {
  const [message, setMessage] = useState<string>("Loading response from Django...");
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    // Client-side fetch
    fetch("http://localhost:8000/api/hello/")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch hello world");
        return res.json();
      })
      .then((data) => setMessage(data.message))
      .catch((err) => {
        console.error(err);
        setError(true);
        setMessage("Failed to connect to backend");
      });
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="rounded-3xl border border-slate-700 bg-slate-900/80 p-10 shadow-xl"
      >
        <h1 className="text-3xl font-bold">Hello from Next.js</h1>
        <p className={`mt-4 ${error ? 'text-red-400' : 'text-slate-300'}`}>
          Django says: {message}
        </p>
      </motion.div>
    </main>
  );
}