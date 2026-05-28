import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Alert from '../components/Alert';
import React from 'react';

/**
 * Component test for Alert.
 * Focus: UI Quality and visual feedback validation.
 */
describe('Alert Component', () => {
  it('renders with correct message', () => {
    render(<Alert type="success" message="Operation successful!" />);
    expect(screen.getByText('Operation successful!')).toBeDefined();
  });

  it('applies the correct CSS class based on type', () => {
    const { container } = render(<Alert type="error" message="Error occurred" />);
    // Check if the div has the 'alert-error' class
    const alertDiv = container.firstChild as HTMLElement;
    expect(alertDiv.className).toContain('alert-error');
  });

  it('calls onClose when close button is clicked', () => {
    const onCloseMock = vi.fn();
    render(<Alert type="info" message="Click me" onClose={onCloseMock} />);
    
    const closeButton = screen.getByLabelText('Fechar alerta');
    closeButton.click();
    
    expect(onCloseMock).toHaveBeenCalledTimes(1);
  });
});
