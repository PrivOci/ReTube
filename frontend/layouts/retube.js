import Head from "next/head";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Content from "../components/Content";
import Footer from "../components/Footer";

export default function Layout({ children }) {
  return (
    <div className="bg-gray-100 dark:bg-gray-600">
      <Head>
        <title>ReTube - Reimagine Tubing</title>
        <meta charSet="utf-8" />
        <meta name="viewport" content="initial-scale=1.0, width=device-width" />
      </Head>
      <Navbar />
      <main className="flex bg-gray-100 dark:bg-gray-800 rounded-2xl overflow-hidden relative">
        <Sidebar />
        <Content>{children}</Content>
      </main>
      <Footer />
    </div>
  );
}
