export function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold">{{PROJECT_NAME}}</h1>
        <p className="mt-4 text-gray-500">
          项目已就绪，开始开发吧！
        </p>
      </div>
    </main>
  );
}
