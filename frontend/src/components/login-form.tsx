"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";

import { login, register } from "@/lib/api";

type Mode = "login" | "register";

export function LoginForm() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [error, setError] = useState<string | null>(null);
  const passwordRef = useRef("");

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      router.push("/dashboard");
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const registerMutation = useMutation({
    mutationFn: register,
    onSuccess: async (user) => {
      await loginMutation.mutateAsync({
        email: user.email,
        password: passwordRef.current,
      });
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const isPending = loginMutation.isPending || registerMutation.isPending;

  return (
    <div className="auth-card auth-card-dark">
      <div className="auth-card-top auth-card-top-centered">
        <div className="stack">
          <h1 className="auth-title">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="auth-subtitle">
            {mode === "login"
              ? "Login to your workspace"
              : "Register once, then continue straight to your dashboard"}
          </p>
        </div>
      </div>

      <form
        className="stack auth-form"
        onSubmit={async (event) => {
          event.preventDefault();
          setError(null);

          const formData = new FormData(event.currentTarget);
          const email = String(formData.get("email") ?? "");
          const password = String(formData.get("password") ?? "");
          passwordRef.current = password;

          if (mode === "login") {
            await loginMutation.mutateAsync({ email, password });
            return;
          }

          await registerMutation.mutateAsync({
            email,
            password,
            given_name: String(formData.get("given_name") ?? ""),
            last_name: String(formData.get("last_name") ?? ""),
          });
        }}
      >
        {mode === "register" ? (
          <div className="grid two">
            <label className="field auth-field">
              <span>Given name</span>
              <input name="given_name" placeholder="Ali" required disabled={isPending} />
            </label>
            <label className="field auth-field">
              <span>Last name</span>
              <input name="last_name" placeholder="Dela Cruz" required disabled={isPending} />
            </label>
          </div>
        ) : null}

        <label className="field auth-field">
          <span>Email</span>
          <input
            name="email"
            type="email"
            placeholder="ali@example.com"
            required
            disabled={isPending}
          />
        </label>

        <div className="auth-field-head">
          <span>Password</span>
          <button className="auth-link-button" type="button">
            Forgot your password?
          </button>
        </div>

        <label className="field auth-field">
          <span className="sr-only">Password</span>
          <input
            name="password"
            type="password"
            placeholder="password123"
            required
            minLength={8}
            disabled={isPending}
          />
        </label>

        {error ? <div className="auth-alert">{error}</div> : null}

        <div className="actions">
          <button className="button auth-primary-button" type="submit" disabled={isPending}>
            {mode === "login"
              ? isPending
                ? "Logging in..."
                : "Log In"
              : isPending
                ? "Creating account..."
                : "Create Account"}
          </button>
        </div>

        <div className="auth-divider">
          <span>Or continue with</span>
        </div>

        <div className="auth-socials">
          <button className="button-secondary auth-social-button" type="button">
            Apple
          </button>
          <button className="button-secondary auth-social-button" type="button">
            Google
          </button>
          <button className="button-secondary auth-social-button" type="button">
            Meta
          </button>
        </div>

        <div className="auth-footer-copy">
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            className="auth-inline-link"
            type="button"
            onClick={() => {
              setError(null);   
              setMode((current) => (current === "login" ? "register" : "login"));
            }}
          >
            {mode === "login" ? "Sign up" : "Log in"}
          </button>
        </div>

        <Link className="auth-minor-link" href="/dashboard">
          Open dashboard shell
        </Link>
      </form>
    </div>
  );
}
