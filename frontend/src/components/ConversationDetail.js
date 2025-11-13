import React, { useState, useEffect, useCallback } from 'react';
import { Card } from './ui/card';
import { API_URL } from '../config';

function ConversationDetail({ conversationId, onBack }) {
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [caseSubmission, setCaseSubmission] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchConversationDetail = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch messages
      const messagesResponse = await fetch(
        `${API_URL}/chatbot/conversations/${conversationId}/`
      );
      const messagesData = await messagesResponse.json();
      
      setConversation({
        id: messagesData.id,
        created_at: messagesData.created_at,
        updated_at: messagesData.updated_at,
        is_complete: messagesData.is_complete
      });
      setMessages(messagesData.messages || []);

      // Try to fetch case submission if conversation is complete
      if (messagesData.is_complete) {
        try {
          const caseResponse = await fetch(
            `${API_URL}/chatbot/conversations/${conversationId}/case_summary/`
          );
          if (caseResponse.ok) {
            const caseData = await caseResponse.json();
            setCaseSubmission(caseData);
          }
        } catch (err) {
          console.log('No case submission found');
        }
      }
    } catch (error) {
      console.error('Error fetching conversation detail:', error);
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  useEffect(() => {
    fetchConversationDetail();
  }, [fetchConversationDetail]);

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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="p-8">
        <Card className="p-12 text-center border border-gray-200">
          <p className="text-gray-600">Conversation not found</p>
          <button onClick={onBack} className="mt-4 text-black hover:text-gray-600">
            ← Back to Conversations
          </button>
        </Card>
      </div>
    );
  }

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
            Back to Conversations
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Conversation</h1>
              <p className="text-gray-600 mt-1 font-mono text-sm">{conversation.id}</p>
            </div>
            <div className="flex items-center gap-3">
              {conversation.is_complete ? (
                <span className="px-4 py-2 rounded-lg text-sm font-semibold bg-green-50 text-green-900 border-2 border-green-200">
                  Completed
                </span>
              ) : (
                <span className="px-4 py-2 rounded-lg text-sm font-semibold bg-yellow-50 text-yellow-900 border-2 border-yellow-200">
                  In Progress
                </span>
              )}
            </div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Started:</span>
              <div className="font-medium text-gray-900">{formatDate(conversation.created_at)}</div>
            </div>
            <div>
              <span className="text-gray-500">Last Updated:</span>
              <div className="font-medium text-gray-900">{formatDate(conversation.updated_at)}</div>
            </div>
            <div>
              <span className="text-gray-500">Messages:</span>
              <div className="font-medium text-gray-900">{messages.length}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 py-6">
        {/* Case Submission Link */}
        {caseSubmission && (
          <Card className="p-6 mb-6 bg-blue-50 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-blue-900 mb-1">Case Submitted</h3>
                <p className="text-sm text-blue-700">
                  Client: {caseSubmission.personal_info?.name || 'Unknown'} • 
                  Urgency: {caseSubmission.urgency_score}/10
                </p>
              </div>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                View Case
              </button>
            </div>
          </Card>
        )}

        {/* Conversation Messages */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversation Transcript</h3>
          <div className="space-y-4 max-h-[600px] overflow-y-auto">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No messages in this conversation</p>
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
      </div>
    </div>
  );
}

export default ConversationDetail;
