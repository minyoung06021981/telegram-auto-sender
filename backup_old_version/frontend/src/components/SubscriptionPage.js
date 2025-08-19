import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const SubscriptionPage = () => {
  const { API, addNotification } = useContext(AppContext);
  const [plans, setPlans] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      const headers = { Authorization: `Bearer ${token}` };

      // Load subscription plans and user info
      const [plansResponse, userResponse] = await Promise.all([
        axios.get(`${API}/subscription/plans`),
        axios.get(`${API}/users/me`, { headers })
      ]);

      setPlans(plansResponse.data);
      setUserInfo(userResponse.data);
    } catch (error) {
      addNotification('Gagal memuat data subscription', 'error');
    }
    setLoading(false);
  };

  const handleUpgrade = async (planId) => {
    try {
      const token = localStorage.getItem('accessToken');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post(`${API}/subscription/upgrade?plan_id=${planId}`, {}, { headers });
      
      addNotification('Subscription berhasil diupgrade!', 'success');
      loadSubscriptionData(); // Reload data
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Upgrade gagal', 'error');
    }
  };

  const PlanCard = ({ plan, isCurrentPlan, isPopular }) => (
    <div className={`relative dashboard-card h-full transition-all duration-300 ${
      isCurrentPlan ? 'ring-2 ring-telegram-blue' : ''
    } ${isPopular ? 'transform scale-105' : ''}`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-gradient-to-r from-telegram-blue to-telegram-accent text-white px-4 py-1 rounded-full text-sm font-semibold">
            ⭐ Paling Populer
          </span>
        </div>
      )}
      
      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2">{plan.name}</h3>
        <p className="text-gray-600 mb-4">{plan.description}</p>
        
        <div className="mb-4">
          {plan.price === 0 ? (
            <span className="text-4xl font-bold text-telegram-blue">Gratis</span>
          ) : (
            <div>
              <span className="text-4xl font-bold text-telegram-blue">${plan.price}</span>
              <span className="text-gray-500 ml-2">/{plan.duration_days <= 30 ? 'bulan' : 'tahun'}</span>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4 mb-8">
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Maksimal Grup:</span>
          <span className="font-semibold">
            {plan.max_groups === 999 ? 'Unlimited' : plan.max_groups}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Pesan per Hari:</span>
          <span className="font-semibold">
            {plan.max_messages_per_day === 9999 ? 'Unlimited' : plan.max_messages_per_day}
          </span>
        </div>
      </div>

      <div className="space-y-3 mb-8">
        {plan.features.map((feature, index) => (
          <div key={index} className="flex items-center">
            <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="text-gray-700">{feature}</span>
          </div>
        ))}
      </div>

      {isCurrentPlan ? (
        <button className="w-full py-3 bg-gray-100 text-gray-600 rounded-lg font-semibold cursor-not-allowed">
          Plan Aktif
        </button>
      ) : (
        <button
          onClick={() => handleUpgrade(plan.id)}
          className={`w-full py-3 rounded-lg font-semibold transition-all ${
            isPopular
              ? 'bg-gradient-to-r from-telegram-blue to-telegram-accent text-white hover:shadow-lg transform hover:-translate-y-1'
              : 'bg-telegram-blue hover:bg-telegram-blue-dark text-white'
          }`}
        >
          {plan.price === 0 ? 'Pilih Plan Gratis' : 'Upgrade Sekarang'}
        </button>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-telegram-blue to-telegram-accent bg-clip-text text-transparent mb-4">
          Pilih Plan Subscription
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upgrade ke Premium untuk fitur unlimited dan dukungan prioritas
        </p>
      </div>

      {/* Current Subscription Info */}
      {userInfo && (
        <div className="dashboard-card bg-gradient-to-r from-telegram-blue/5 to-telegram-accent/5 border-telegram-blue/20">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Status Subscription</h3>
              <p className="text-gray-600">
                Plan saat ini: <span className="font-semibold text-telegram-blue capitalize">
                  {userInfo.subscription_type}
                </span>
              </p>
              {userInfo.subscription_expires && (
                <p className="text-sm text-gray-500">
                  Berakhir: {new Date(userInfo.subscription_expires).toLocaleDateString('id-ID')}
                </p>
              )}
            </div>
            <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
              userInfo.subscription_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {userInfo.subscription_active ? '✅ Aktif' : '❌ Tidak Aktif'}
            </div>
          </div>
        </div>
      )}

      {/* Subscription Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan, index) => (
          <PlanCard
            key={plan.id}
            plan={plan}
            isCurrentPlan={userInfo?.subscription_type === plan.name.toLowerCase()}
            isPopular={plan.name === 'Premium'}
          />
        ))}
      </div>

      {/* FAQ Section */}
      <div className="dashboard-card">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Frequently Asked Questions</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Bagaimana cara upgrade subscription?</h3>
            <p className="text-gray-600">
              Klik tombol "Upgrade Sekarang" pada plan yang diinginkan. Pembayaran akan diproses secara otomatis.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Apakah bisa downgrade plan?</h3>
            <p className="text-gray-600">
              Ya, Anda bisa downgrade plan kapan saja melalui halaman pengaturan akun.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Apakah ada trial period?</h3>
            <p className="text-gray-600">
              Plan Free sudah tersedia tanpa batas waktu. Anda bisa mencoba semua fitur dasar secara gratis.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPage;