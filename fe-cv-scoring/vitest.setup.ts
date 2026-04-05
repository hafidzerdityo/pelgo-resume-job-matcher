import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock timers globally for polling tests
vi.useFakeTimers();
