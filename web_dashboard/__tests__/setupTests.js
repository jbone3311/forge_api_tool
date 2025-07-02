/**
 * Jest setup file for dashboard tests
 */

// Mock fetch globally with proper response structure
global.fetch = jest.fn(() => Promise.resolve({
  ok: true,
  status: 200,
  json: () => Promise.resolve({}),
  text: () => Promise.resolve(''),
  headers: new Map(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Polyfill TextEncoder/TextDecoder for Jest
try {
  const { TextEncoder, TextDecoder } = require('util');
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
} catch (e) {
  // Already defined or not needed
}

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Setup before each test
beforeEach(() => {
  // Clear all mocks
  jest.clearAllMocks();
  
  // Reset fetch mock
  fetch.mockClear();
  
  // Reset localStorage
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
  
  // Reset sessionStorage
  sessionStorageMock.getItem.mockClear();
  sessionStorageMock.setItem.mockClear();
  sessionStorageMock.removeItem.mockClear();
  sessionStorageMock.clear.mockClear();
  
  // Reset console mocks
  console.log.mockClear();
  console.debug.mockClear();
  console.info.mockClear();
  console.warn.mockClear();
  console.error.mockClear();
});

// Helper function to create a mock DOM element
global.createMockElement = (tagName = 'div', attributes = {}) => {
  const element = document.createElement(tagName);
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value);
  });
  return element;
};

// Helper function to simulate user events
global.simulateEvent = (element, eventType, options = {}) => {
  const event = new Event(eventType, { bubbles: true, cancelable: true, ...options });
  element.dispatchEvent(event);
  return event;
};

// Helper function to simulate keyboard events
global.simulateKeyEvent = (element, key, options = {}) => {
  const event = new KeyboardEvent('keydown', {
    key,
    bubbles: true,
    cancelable: true,
    ...options
  });
  element.dispatchEvent(event);
  return event;
};

// Helper function to simulate mouse events
global.simulateMouseEvent = (element, eventType, options = {}) => {
  const event = new MouseEvent(eventType, {
    bubbles: true,
    cancelable: true,
    ...options
  });
  element.dispatchEvent(event);
  return event;
};

// Helper function to wait for async operations
global.waitFor = (callback, timeout = 1000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      try {
        const result = callback();
        if (result) {
          resolve(result);
          return;
        }
      } catch (error) {
        // Continue checking
      }
      
      if (Date.now() - startTime > timeout) {
        reject(new Error(`waitFor timed out after ${timeout}ms`));
        return;
      }
      
      setTimeout(check, 10);
    };
    
    check();
  });
};

// Helper function to create a mock fetch response
global.createMockResponse = (data, status = 200, ok = true) => {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: new Map(),
  });
};

// Helper function to create a mock fetch error
global.createMockError = (message = 'Network error') => {
  return Promise.reject(new Error(message));
};

// Helper function to mock fetch for specific endpoints
global.mockFetchEndpoint = (endpoint, response, status = 200, ok = true) => {
  fetch.mockImplementation((url) => {
    if (url === endpoint || url.includes(endpoint)) {
      return Promise.resolve({
        ok,
        status,
        json: () => Promise.resolve(response),
        text: () => Promise.resolve(JSON.stringify(response)),
        headers: new Map(),
      });
    }
    // Default response for other endpoints
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
      headers: new Map(),
    });
  });
};

// Helper function to create proper JSDOM events
global.createJSDOMEvent = (type, options = {}) => {
  if (type === 'keydown' || type === 'keyup' || type === 'keypress') {
    return new KeyboardEvent(type, {
      bubbles: true,
      cancelable: true,
      ...options
    });
  } else if (type === 'click' || type === 'mousedown' || type === 'mouseup') {
    return new MouseEvent(type, {
      bubbles: true,
      cancelable: true,
      ...options
    });
  } else {
    return new Event(type, {
      bubbles: true,
      cancelable: true,
      ...options
    });
  }
}; 