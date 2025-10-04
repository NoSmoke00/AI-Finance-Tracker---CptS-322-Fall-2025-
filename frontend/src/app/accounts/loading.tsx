import AppLayout from '@/components/AppLayout';

export default function Loading() {
  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Bank Accounts</h1>
              <p className="text-gray-600">Loading...</p>
            </div>
            <div className="h-10 bg-gray-300 rounded w-32 animate-pulse"></div>
          </div>
        </div>

        <main className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gray-300 rounded-full animate-pulse"></div>
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="h-5 bg-gray-300 rounded w-32 mb-2 animate-pulse"></div>
                    <div className="h-4 bg-gray-300 rounded w-24 mb-1 animate-pulse"></div>
                    <div className="h-4 bg-gray-300 rounded w-28 animate-pulse"></div>
                  </div>
                </div>
                
                <div className="mt-4">
                  <div className="flex justify-between items-center">
                    <div className="h-4 bg-gray-300 rounded w-24 animate-pulse"></div>
                    <div className="h-5 bg-gray-300 rounded w-20 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        </main>
      </div>
    </AppLayout>
  );
}
