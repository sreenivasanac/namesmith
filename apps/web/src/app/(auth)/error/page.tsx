import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface AuthErrorPageProps {
  searchParams: { error?: string };
}

export default async function AuthErrorPage({ searchParams }: AuthErrorPageProps) {
  const error = searchParams.error;

  const getErrorMessage = (error?: string) => {
    switch (error) {
      case "auth_failed":
        return "Authentication failed. The magic link may have expired. Please try again.";
      case "otp_expired":
        return "The magic link has expired. Please request a new one.";
      case "access_denied":
        return "Access was denied. Please try again.";
      case "unexpected_error":
        return "An unexpected error occurred. Please try again.";
      case "no_code":
        return "Invalid authentication link. Please try logging in again.";
      default:
        return "An authentication error occurred. Please try again.";
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Authentication Error</CardTitle>
          <CardDescription>
            {getErrorMessage(error)}
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <Link href="/login">
            <Button className="w-full">
              Try Again
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
