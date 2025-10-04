import AppLayout from '@/components/AppLayout';

export default function Loading() {
  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        <main className="p-6">
        {/* Loading Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-gray-300 rounded-full animate-pulse"></div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <div className="h-4 bg-gray-300 rounded w-24 mb-2 animate-pulse"></div>
                    <div className="h-6 bg-gray-300 rounded w-16 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Loading Accounts */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Accounts
              </h3>
              <div className="space-y-4">
                <div className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="h-4 bg-gray-300 rounded w-32 mb-2 animate-pulse"></div>
                      <div className="h-3 bg-gray-300 rounded w-48 animate-pulse"></div>
                    </div>
                    <div className="h-4 bg-gray-300 rounded w-20 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Loading Transactions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Recent Transactions
              </h3>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex justify-between items-center py-2 border-b last:border-b-0">
                    <div>
                      <div className="h-4 bg-gray-300 rounded w-32 mb-1 animate-pulse"></div>
                      <div className="h-3 bg-gray-300 rounded w-24 animate-pulse"></div>
                    </div>
                    <div className="h-4 bg-gray-300 rounded w-16 animate-pulse"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        </main>
      </div>
    </AppLayout>
  );
}
