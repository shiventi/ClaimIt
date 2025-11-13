import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { ArrowUp } from 'lucide-react';
import claimItLogo from '../claimit.png';
import claimItAvatar from '../claimitavatar.png';
import { API_URL } from '../config';

console.log('Chat component loaded. API_URL:', API_URL);

const Chat = ({ conversationId, onCreateConversation }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 25 });
  const [isComplete, setIsComplete] = useState(false);
  const [isMultiline, setIsMultiline] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const inputContainerRef = useRef(null);

  const startNewConversation = async () => {
    // Clear current conversation
    setMessages([]);
    setProgress({ current: 0, total: 25 });
    setIsComplete(false);
    setInputMessage('');
    
    // Clear from localStorage
    localStorage.removeItem('currentConversationId');
    
    // Create new conversation
    if (onCreateConversation) {
      await onCreateConversation();
    }
  };

  useEffect(() => {
    if (isComplete) {
      // Clear conversation ID from localStorage when conversation is complete
      localStorage.removeItem('currentConversationId');
    }
  }, [isComplete]);

  // Auto-resize textarea and check for multiline
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const singleRowHeight = textareaRef.current.offsetHeight;
      
      const isMulti = scrollHeight > singleRowHeight + 5; 
      setIsMultiline(isMulti);
      
      textareaRef.current.style.height = Math.min(scrollHeight, 150) + 'px';
    }
  }, [inputMessage]);

  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }

    let cancelled = false;

    const fetchConversation = async () => {
      try {
        const response = await fetch(
          `${API_URL}/chatbot/conversations/${conversationId}/`
        );

        if (!response.ok) {
          throw new Error(`Failed to load conversation: ${response.status}`);
        }

        const data = await response.json();
        if (cancelled) return;

        setMessages(data.messages || []);
        setIsComplete(data.is_complete || false);
      } catch (error) {
        console.error('Error loading conversation:', error);
      }
    };

    fetchConversation();

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Create conversation if it doesn't exist yet
    let currentConvId = conversationId;
    if (!currentConvId && onCreateConversation) {
      currentConvId = await onCreateConversation();
      if (!currentConvId) {
        console.error('Failed to create conversation');
        setIsLoading(false);
        return;
      }
    }

    const newUserMessage = { role: 'user', content: userMessage, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, newUserMessage]);

    setTimeout(() => setIsTyping(true), 300);

    try {
      console.log('Sending message to:', `${API_URL}/chatbot/conversations/${currentConvId}/send_message/`);
      console.log('Message content:', userMessage);
      
      const response = await fetch(
        `${API_URL}/chatbot/conversations/${currentConvId}/send_message/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userMessage }),
        }
      );

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error text:', errorText);
        throw new Error(`Request failed with status ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.messages) {
        setMessages(data.messages);
      }
      
      if (data.questions_asked) {
        setProgress({ 
          current: Math.min(data.questions_asked, 25), 
          total: 25 
        });
      }
      
      if (data.is_complete) {
        setIsComplete(true);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        { 
          role: 'assistant', 
          content: 'I apologize, but I am having trouble connecting right now. Please try again in a moment.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setIsTyping(false);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const progressPercentage = progress.total > 0 ? (progress.current / progress.total) * 100 : 0;

  return (
    <div className="flex flex-col h-full bg-white">
      <style>
        {`
          textarea::-webkit-scrollbar {
            display: none;
          }
        `}
      </style>
      {/* Header */}
      <div className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-3">
            <div 
              className="h-10 flex items-center justify-center flex-shrink-0 cursor-pointer"
              onClick={() => window.location.reload()}
            >
              <img 
                src={claimItLogo} 
                alt="ClaimIt" 
                className="h-8 w-auto object-contain select-none"
                draggable="false"
              />
            </div>
          </div>
          
          {!isComplete && progress.current > 0 && (
            <div className="mt-4 space-y-2">
              <Progress value={progressPercentage} className="h-1.5" />
              <p className="text-xs text-gray-400 text-right">
                Question {progress.current} of ~{progress.total}
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {messages.length === 0 && (
            <div className="flex items-center justify-center min-h-[50vh]">
              <div className="text-center max-w-md px-4">
                <div className="w-16 h-16 rounded-full bg-black flex items-center justify-center mx-auto mb-6 overflow-hidden">
                  <img src={claimItAvatar} alt="ClaimIt" className="w-full h-full object-cover" />
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">Welcome to ClaimIt</h2>
                <p className="text-sm sm:text-base text-gray-600 mb-3">
                  I'm here to help you access government benefits like food assistance, healthcare coverage, and financial support.
                </p>
                <p className="text-sm sm:text-base text-gray-600 mb-3">
                  This conversation is <span className="font-semibold">confidential</span> and will take about <span className="font-semibold">10-15 minutes</span>.
                </p>
                <p className="text-xs sm:text-sm text-gray-500 mt-6">
                  Type your message below to start
                </p>
              </div>
            </div>
          )}
          
          <div className="space-y-6">
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`flex gap-3 sm:gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full overflow-hidden">
                    <img src={claimItAvatar} alt="ClaimIt AI" className="w-full h-full object-cover" />
                  </div>
                )}
                
                <div className={`flex flex-col max-w-[85%] sm:max-w-[75%] ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div 
                    className={`rounded-2xl px-4 sm:px-5 py-3 sm:py-3.5 ${
                      message.role === 'assistant' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'bg-black text-white'
                    }`}
                  >
                    {message.role === 'assistant' ? (
                      <div className="prose prose-sm max-w-none prose-p:my-1.5 prose-p:leading-relaxed prose-ul:my-2 prose-li:my-1 text-gray-900">
                        <ReactMarkdown
                          components={{
                            p: ({node, ...props}) => <p className="whitespace-pre-wrap" {...props} />,
                            ul: ({node, ...props}) => <ul className="space-y-1 ml-0 list-none" {...props} />,
                            li: ({node, ...props}) => <li className="leading-relaxed" {...props} />
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="text-sm sm:text-base whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </div>
                    )}
                  </div>
                  {message.created_at && (
                    <span className="text-xs text-gray-400 mt-1.5 px-2">
                      {new Date(message.created_at).toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </span>
                  )}
                </div>
                
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <div className="text-sm sm:text-base font-semibold text-gray-700">You</div>
                  </div>
                )}
              </div>
            ))}
            
            {isTyping && (
              <div className="flex gap-3 sm:gap-4 justify-start">
                <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full overflow-hidden">
                  <img src={claimItAvatar} alt="ClaimIt AI" className="w-full h-full object-cover" />
                </div>
                <div className="bg-gray-100 rounded-2xl px-5 py-3">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      {/* Input Area */}
      <div className="bg-white sticky bottom-0" ref={inputContainerRef}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {isComplete && (
            <div className="bg-gray-100 border border-gray-200 rounded-2xl px-4 py-3 mb-4 text-sm sm:text-base text-gray-800">
              <div className="flex items-center justify-between">
                <span>Your intake is complete. A caseworker will review your information and contact you within 48 hours.</span>
                <Button 
                  onClick={startNewConversation}
                  className="ml-4 bg-black hover:bg-gray-800 text-white px-4 py-2 text-sm"
                >
                  Start New Conversation
                </Button>
              </div>
            </div>
          )}
          
          {!isComplete && (
            <form onSubmit={handleSendMessage} className="space-y-2">
              <div className="relative">
                  <textarea
                    ref={textareaRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message here..."
                    className="w-full resize-none rounded-3xl border border-gray-300 px-4 py-3 pr-12 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                    rows="1"
                    disabled={isLoading}
                    style={{ 
                      minHeight: '50px', 
                      maxHeight: '150px'
                    }}
                  />
                  <Button 
                    type="submit" 
                    size="icon"
                    disabled={!inputMessage.trim() || isLoading}
                    className={`absolute rounded-full w-9 h-9 p-0 bg-black hover:bg-gray-800 disabled:bg-gray-300 ${
                      isMultiline 
                        ? 'right-2 bottom-2' 
                        : 'right-2 top-1/2 -translate-y-1/2'
                    }`}
                  >
                    <ArrowUp className="h-4 w-4" />
                  </Button>
                </div>
              <p className="text-xs text-gray-400 text-center px-2">
                Press Enter to send • Shift+Enter for new line
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;