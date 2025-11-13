import React, { useEffect, useState } from 'react';
import './FormViewer.css';
import { API_URL } from '../config';

const FormViewer = ({ formName, formData, conversationId }) => {
  if (!formName) {
    return (
      <div className="form-viewer-container">
        <div className="no-form">
          <h3>No Form Selected</h3>
          <p>Complete the conversation to see your recommended form</p>
        </div>
      </div>
    );
  }

  // Handle case where user is not eligible (formName = 'NONE')
  if (formName === 'NONE') {
    return (
      <div className="form-viewer-container">
        <div style={{
          padding: '30px',
          background: '#fff5f0',
          borderRadius: '8px',
          border: '2px solid #e29d4a',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#a06a2c', marginTop: 0 }}>⚠️ Eligibility Assessment Complete</h2>
          <p style={{ fontSize: '16px', lineHeight: '1.6', marginBottom: '20px' }}>
            Based on the information you've provided, you may not currently qualify for the government benefit programs we screen for.
          </p>
          
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '8px',
            marginTop: '20px',
            textAlign: 'left'
          }}>
            <h3 style={{ marginTop: 0, color: '#2c5aa0' }}>📊 Your Information:</h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
              gap: '10px', 
              fontSize: '14px' 
            }}>
              {formData?.name && <div><strong>Name:</strong> {formData.name}</div>}
              {formData?.age && <div><strong>Age:</strong> {formData.age}</div>}
              {formData?.household_size !== undefined && <div><strong>Household:</strong> {formData.household_size} {formData.household_size === 1 ? 'person' : 'people'}</div>}
              {formData?.monthly_income !== undefined && <div><strong>Monthly Income:</strong> ${formData.monthly_income}</div>}
            </div>
          </div>

          <div style={{
            background: '#e8f5e9',
            padding: '20px',
            borderRadius: '8px',
            marginTop: '20px',
            textAlign: 'left'
          }}>
            <h3 style={{ marginTop: 0, color: '#2e7d32' }}>💡 Alternative Resources:</h3>
            <ul style={{ fontSize: '15px', lineHeight: '1.8' }}>
              <li><strong>Food Banks:</strong> Many local food banks don't have income requirements - search "food bank near me"</li>
              <li><strong>211 Helpline:</strong> Dial 2-1-1 for local community resources and assistance programs</li>
              <li><strong>Community Organizations:</strong> Churches, nonprofits, and community centers often provide assistance</li>
              <li><strong>Payment Plans:</strong> Many utilities and services offer payment assistance programs</li>
              <li><strong>Future Eligibility:</strong> If your circumstances change (job loss, medical issues), you may qualify later</li>
            </ul>
          </div>

          <p style={{ marginTop: '20px', fontSize: '14px', fontStyle: 'italic', color: '#666' }}>
            Remember: Eligibility requirements can change, and your situation may qualify you in the future. 
            Keep this information and don't hesitate to check again if things change.
          </p>
        </div>
      </div>
    );
  }

  const formTitles = {
    'SNAP': 'CalFresh (Food Assistance)',
    'MEDICAL': 'Medi-Cal (Healthcare Coverage)',
    'SSI': 'SSI (Supplemental Security Income)',
    'TANF': 'CalWORKs (Cash Assistance for Families)',
    'WIC': 'WIC (Women, Infants, and Children)'
  };

  const formDescriptions = {
    'SNAP': 'Helps low-income individuals and families buy nutritious food',
    'MEDICAL': 'Provides free or low-cost health coverage for eligible California residents',
    'SSI': 'Provides monthly cash payments to elderly or disabled individuals with limited income',
    'TANF': 'Provides temporary cash assistance and support services to families with children',
    'WIC': 'Provides nutrition assistance for pregnant women, new mothers, and children under 5'
  };

  // Handle multiple forms (comma-separated)
  const formsList = formName ? formName.split(',').map(f => f.trim()) : [];

  return (
    <div className="form-viewer-container">
      <div className="form-header">
        <h2>📋 Recommended Form{formsList.length > 1 ? 's' : ''}</h2>
        <p style={{ margin: '10px 0', fontSize: '16px' }}>
          Based on your information, we recommend you apply for the following benefit{formsList.length > 1 ? 's' : ''}:
        </p>
      </div>

      <div className="info-summary" style={{ 
        padding: '20px', 
        background: '#f0f8ff', 
        borderRadius: '8px', 
        marginBottom: '20px',
        border: '2px solid #4a90e2'
      }}>
        <h3 style={{ marginTop: 0, color: '#2c5aa0' }}>Your Information Summary</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
          gap: '15px' 
        }}>
          {formData?.name && (
            <div><strong>Name:</strong> {formData.name}</div>
          )}
          {formData?.age && (
            <div><strong>Age:</strong> {formData.age}</div>
          )}
          {formData?.household_size !== undefined && (
            <div><strong>Household Size:</strong> {formData.household_size} {formData.household_size === 1 ? 'person' : 'people'}</div>
          )}
          {formData?.monthly_income !== undefined && (
            <div><strong>Monthly Income:</strong> ${formData.monthly_income}</div>
          )}
          {formData?.assets !== undefined && (
            <div><strong>Assets:</strong> ${formData.assets}</div>
          )}
          {formData?.is_employed !== undefined && (
            <div><strong>Employment:</strong> {formData.is_employed ? 'Employed' : 'Unemployed'}</div>
          )}
          {formData?.has_children !== undefined && (
            <div><strong>Children:</strong> {formData.has_children ? 'Yes' : 'No'}</div>
          )}
          {formData?.has_disability !== undefined && (
            <div><strong>Disability:</strong> {formData.has_disability ? 'Yes' : 'No'}</div>
          )}
        </div>
      </div>

      {formsList.map((form, index) => (
        <div key={form} style={{
          padding: '25px',
          background: index % 2 === 0 ? '#f0f8ff' : '#fff5f0',
          borderRadius: '8px',
          marginBottom: '15px',
          border: `2px solid ${index % 2 === 0 ? '#4a90e2' : '#e29d4a'}`
        }}>
          <h3 style={{ marginTop: 0, color: index % 2 === 0 ? '#2c5aa0' : '#a06a2c' }}>
            {formsList.length > 1 ? `${index + 1}. ` : ''}{formTitles[form] || form}
          </h3>
          <p style={{ marginBottom: '15px', fontStyle: 'italic', fontSize: '15px' }}>
            {formDescriptions[form] || 'Government assistance program'}
          </p>
          <button 
            className="btn-primary"
            style={{
              padding: '12px 30px',
              fontSize: '16px',
              background: index % 2 === 0 ? '#4a90e2' : '#e29d4a',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
            onClick={() => {
              alert('PDF functionality has been removed. Please use the dashboard for case management.');
            }}
          >
            📄 PDF Forms Removed - Use Dashboard
          </button>
        </div>
      ))}

      <div style={{ marginTop: '20px', padding: '20px', background: '#fffef0', borderRadius: '6px' }}>
        <h4 style={{ marginTop: 0, color: '#856404' }}>💡 Next Steps:</h4>
        <ol style={{ textAlign: 'left', fontSize: '15px' }}>
          <li>Download the form(s) using the button(s) above</li>
          <li>Fill out each form carefully with your information (see summary above)</li>
          <li>Gather required documents (ID, proof of income, proof of residence, etc.)</li>
          <li>Submit the completed form(s) to your local county office or online</li>
          <li>Wait for notification about your application status (usually 30 days)</li>
        </ol>
      </div>

      <div className="form-download-section" style={{
        padding: '0px',
        background: 'transparent',
        display: 'none'
      }}>
        <h3>📥 Download Your Form</h3>
        <p style={{ marginBottom: '20px', fontSize: '15px' }}>
          Click below to download the blank {formTitles[formName] || formName} application form. 
          You'll need to fill it out with the information provided above.
        </p>
        
        <button 
          className="btn-primary"
          style={{
            padding: '15px 40px',
            fontSize: '18px',
            background: '#4a90e2',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
          onClick={() => {
            alert('PDF functionality has been removed. Please use the dashboard for case managment.');
          }}
        >
          📄 PDF Forms Removed - Use Dashboard
        </button>

        <div style={{ marginTop: '30px', padding: '20px', background: '#fffef0', borderRadius: '6px' }}>
          <h4 style={{ marginTop: 0, color: '#856404' }}>💡 Next Steps:</h4>
          <ol style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
            <li>Download the form using the button above</li>
            <li>Fill out the form with your information (see summary above)</li>
            <li>Gather required documents (ID, proof of income, etc.)</li>
            <li>Submit the completed form to your local county office</li>
            <li>Wait for notification about your application status</li>
          </ol>
        </div>
      </div>

      <div className="form-instructions" style={{ marginTop: '20px', padding: '15px', background: '#e8f5e9', borderRadius: '6px' }}>
        <p style={{ margin: 0 }}>
          ✅ You've completed the screening process! The form recommendation is based on your specific needs and situation.
        </p>
      </div>
    </div>
  );
};

export default FormViewer;
