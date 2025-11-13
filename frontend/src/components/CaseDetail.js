import React, { useState, useEffect, useCallback } from 'react';
import { Card } from './ui/card';
import { API_URL } from '../config';

function CaseDetail({ caseId, onBack }) {
  const [caseData, setCase] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchCaseDetail = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/chatbot/dashboard/cases/${caseId}/`);
      const data = await response.json();
      setCase(data.case);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching case detail:', error);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchCaseDetail();
  }, [fetchCaseDetail]);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return 'N/A';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  const getUrgencyColor = (score) => {
    if (score >= 8) return 'bg-red-50 text-red-900 border-red-300';
    if (score >= 6) return 'bg-orange-50 text-orange-900 border-orange-300';
    if (score >= 4) return 'bg-yellow-50 text-yellow-900 border-yellow-300';
    return 'bg-green-50 text-green-900 border-green-300';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="p-8">
        <Card className="p-12 text-center">
          <p className="text-gray-600">Case not found</p>
          <button onClick={onBack} className="mt-4 text-indigo-600 hover:text-indigo-800">
            ← Back to Cases
          </button>
        </Card>
      </div>
    );
  }

  const InfoRow = ({ label, value, icon }) => (
    <div className="flex items-start py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center text-gray-500 w-48 flex-shrink-0">
        {icon && <span className="mr-2">{icon}</span>}
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="text-gray-900 flex-1">{value || 'N/A'}</div>
    </div>
  );

  const Section = ({ title, children, icon }) => (
    <Card className="p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        {icon && <span className="mr-2">{icon}</span>}
        {title}
      </h3>
      <div className="space-y-1">
        {children}
      </div>
    </Card>
  );

  return (
    <div className="h-full overflow-auto bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-8 py-6">
          <button
            onClick={onBack}
            className="text-black hover:text-gray-600 mb-4 flex items-center text-sm font-medium"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Cases
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{caseData.full_name || 'Unknown Client'}</h1>
              <p className="text-gray-600 mt-1">Submitted {formatDate(caseData.submitted_at)}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-4 py-2 rounded-lg text-sm font-semibold border-2 ${getUrgencyColor(caseData.urgency_score)}`}>
                Urgency: {caseData.urgency_score}/10
              </span>
              {caseData.has_emergency_needs && (
                <span className="px-4 py-2 rounded-lg text-sm font-semibold bg-red-600 text-white">
                  EMERGENCY
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="px-8 flex space-x-8 border-t border-gray-200">
          {['overview', 'conversation', 'recommendations'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-2 border-b-2 font-medium text-sm capitalize transition-colors ${
                activeTab === tab
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="px-8 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Urgency Assessment */}
            {caseData.urgency_reasoning && (
              <Card className="p-6 mb-6 bg-yellow-50 border-yellow-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Urgency Assessment
                </h3>
                <p className="text-gray-800">{caseData.urgency_reasoning}</p>
              </Card>
            )}

            {/* Personal Information */}
            <Section 
              title="Personal Information"
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>}
            >
              <InfoRow label="Full Name" value={caseData.full_name} />
              <InfoRow label="Date of Birth" value={caseData.date_of_birth} />
              <InfoRow label="Age" value={caseData.age} />
              <InfoRow label="Email" value={caseData.email} />
              <InfoRow label="Phone" value={caseData.phone_number} />
            </Section>

            {/* Household Information */}
            <Section 
              title="Household Information"
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>}
            >
              <InfoRow label="Household Size" value={caseData.household_size} />
              <InfoRow label="Has Children" value={caseData.has_children ? 'Yes' : 'No'} />
              {caseData.household_members && caseData.household_members.length > 0 && (
                <div className="py-3">
                  <div className="text-sm font-medium text-gray-500 mb-2">Household Members:</div>
                  <ul className="space-y-1 ml-4">
                    {caseData.household_members.map((member, idx) => (
                      <li key={idx} className="text-sm text-gray-700">
                        {typeof member === 'string' ? member : `${member.name} (${member.age}, ${member.relationship})`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Section>

            {/* Financial Information */}
            <Section 
              title="Financial Information"
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>}
            >
              <InfoRow label="Monthly Income" value={formatCurrency(caseData.monthly_income)} />
              <InfoRow label="Total Assets" value={formatCurrency(caseData.total_assets)} />
              <InfoRow label="Monthly Rent" value={formatCurrency(caseData.monthly_rent)} />
              {caseData.income_sources && caseData.income_sources.length > 0 && (
                <InfoRow label="Income Sources" value={caseData.income_sources.join(', ')} />
              )}
            </Section>

            {/* Employment */}
            <Section 
              title="Employment"
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>}
            >
              <InfoRow label="Status" value={caseData.employment_status} />
              <InfoRow label="Employer" value={caseData.current_employer} />
              <InfoRow label="Job Title" value={caseData.job_title} />
              <InfoRow label="Duration" value={caseData.employment_duration} />
            </Section>

            {/* Housing */}
            <Section 
              title="Housing"
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>}
            >
              <InfoRow label="Situation" value={caseData.housing_situation} />
              <InfoRow label="Address" value={caseData.address} />
              <InfoRow label="At Risk of Homelessness" value={caseData.at_risk_of_homelessness ? 'Yes' : 'No'} />
            </Section>

            {/* Health */}
            <Section 
              title="Health Information"
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>}
            >
              <InfoRow label="Has Disability" value={caseData.has_disability ? 'Yes' : 'No'} />
              {caseData.disability_details && (
                <InfoRow label="Disability Details" value={caseData.disability_details} />
              )}
              <InfoRow label="Has Health Insurance" value={caseData.has_health_insurance ? 'Yes' : 'No'} />
              <InfoRow label="Has Medical Expenses" value={caseData.has_medical_expenses ? 'Yes' : 'No'} />
              <InfoRow label="Monthly Medical Costs" value={formatCurrency(caseData.monthly_medical_costs)} />
            </Section>

            {/* Current Benefits */}
            {caseData.current_benefits && caseData.current_benefits.length > 0 && (
              <Section 
                title="Current Benefits"
                icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>}
              >
                <div className="flex flex-wrap gap-2 py-2">
                  {caseData.current_benefits.map((benefit, idx) => (
                    <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {benefit}
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {/* Emergency Needs */}
            {caseData.has_emergency_needs && caseData.emergency_details && (
              <Card className="p-6 bg-red-50 border-red-200">
                <h3 className="text-lg font-semibold text-red-900 mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Emergency Needs
                </h3>
                <p className="text-red-800">{caseData.emergency_details}</p>
              </Card>
            )}
          </>
        )}

        {/* Conversation Tab */}
        {activeTab === 'conversation' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Full Conversation Transcript</h3>
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {messages.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No messages found</p>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[70%] rounded-lg p-4 ${
                      msg.role === 'user' 
                        ? 'bg-black text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <div className="text-xs opacity-75 mb-1">
                        {msg.role === 'user' ? 'Client' : 'Assistant'} • {formatDate(msg.created_at)}
                      </div>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        )}

        {/* Recommendations Tab */}
        {activeTab === 'recommendations' && (
          <>
            {/* AI Summary */}
            {caseData.ai_summary && (
              <Card className="p-6 mb-6 bg-gray-50 border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  AI-Generated Summary
                </h3>
                <p className="text-gray-900 whitespace-pre-wrap">{caseData.ai_summary}</p>
              </Card>
            )}

            {/* Recommended Programs */}
            {caseData.recommended_programs && caseData.recommended_programs.length > 0 && (
              <Card className="p-6 mb-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Recommended Programs
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {caseData.recommended_programs.map((program, idx) => (
                    <div key={idx} className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <div className="font-semibold text-gray-900">{program}</div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Recommended Actions */}
            {caseData.recommended_actions && (
              <Card className="p-6 bg-gray-50 border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Recommended Next Actions
                </h3>
                <p className="text-gray-900 whitespace-pre-wrap">{caseData.recommended_actions}</p>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default CaseDetail;
