import "tailwindcss/tailwind.css";
import Layout from "../layouts/retube";

function MyApp({ Component, pageProps }) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}

export default MyApp;
