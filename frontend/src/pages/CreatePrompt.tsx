import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import PromptEditor from '../components/PromptEditor';

const CreatePrompt: React.FC = () => {
  const navigate = useNavigate();

  const handleSave = (prompt: any) => {
    if (prompt) {
      navigate(`/prompts/${prompt.id}`);
    }
  };

  const handleCancel = () => {
    navigate('/prompts');
  };

  return (
    <>
      <Header />
      <div className="page-container">
        <PromptEditor isNew={true} onSave={handleSave} onCancel={handleCancel} />
      </div>
    </>
  );
};

export default CreatePrompt;
