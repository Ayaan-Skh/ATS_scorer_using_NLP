"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function NavBar() {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="flex justify-center gap-8 py-6 text-sm font-medium bg-white/10 backdrop-blur-lg border-b border-white/20"
    >
      <Link href="/" className="hover:text-purple-400 transition">Home</Link>
      <Link href="/upload" className="hover:text-purple-400 transition">Upload Resume</Link>
      <Link href="/job" className="hover:text-purple-400 transition">Job Description</Link>
      <Link href="/score" className="hover:text-purple-400 transition">ATS Score</Link>
    </motion.nav>
  );
}
