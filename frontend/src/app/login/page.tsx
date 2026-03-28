import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <main className="auth-shell">
      <section className="auth-frame fade-up">
        <div className="auth-left">
          <LoginForm />
        </div>

        <aside className="auth-right">
          <div className="auth-right-overlay" />
          <div className="auth-right-mark">
            {/* <div className="auth-right-ring auth-right-ring-outer" />
            <div className="auth-right-ring auth-right-ring-inner" /> */}
            {/* <div className="auth-right-core">TJ</div> */}
          </div>
          <div className="auth-right-copy">
            <span className="small auth-kicker"></span>
            <h2>Track long-form transcription jobs without blocking the API.</h2>
            <p>
              Sign in through the frontend, upload media, and let the queue plus worker pipeline
              handle the heavy processing.
            </p>
          </div>
        </aside>
      </section>

      
    </main>
  );
}
