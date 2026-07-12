"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";

import { useAuth } from "./providers";

export default function HomePage() {
  const { user, loading, logout } = useAuth();
  const [message, setMessage] = useState<string>("Loading response from Django...");
  const [helloError, setHelloError] = useState<boolean>(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/hello/")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch hello world");
        return res.json();
      })
      .then((data) => setMessage(data.message))
      .catch((err) => {
        console.error(err);
        setHelloError(true);
        setMessage("Failed to connect to backend");
      });
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900/80 p-10 shadow-xl"
      >
        <h1 className="text-3xl font-bold">Hello from Next.js</h1>
        <p className={`mt-4 ${helloError ? "text-red-400" : "text-slate-300"}`}>
          Django says: {message}
        </p>

        <div className="mt-8 border-t border-slate-700 pt-6 text-sm text-slate-300">
          {loading ? (
            <p className="text-slate-500">Checking session…</p>
          ) : user ? (
            <div className="flex items-center justify-between gap-4">
              <span>
                Logged in as <span className="text-white">{user.email}</span>
              </span>
              <button
                onClick={logout}
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between gap-4">
              <span className="text-slate-500">Not logged in.</span>
              <div className="flex gap-2">
                <Link
                  href="/login"
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
                >
                  Log in
                </Link>
                <Link
                  href="/signup"
                  className="rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-slate-900 hover:bg-slate-200"
                >
                  Sign up
                </Link>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </main>
  );
}
