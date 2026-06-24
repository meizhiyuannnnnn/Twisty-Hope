import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300">404</h1>
        <p className="mt-4 text-gray-500">页面未找到</p>
        <Link to="/" className="mt-6 inline-block text-blue-500 hover:text-blue-600">
          返回首页
        </Link>
      </div>
    </main>
  );
}
