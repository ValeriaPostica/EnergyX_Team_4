export const fetchWithAuth = async (url, options = {}) => {
    const token = localStorage.getItem('token');

    console.log('fetchWithAuth called for:', url);
    console.log('Token exists:', !!token);

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    console.log('Response status:', response.status, 'for', url);

    // If token is invalid, redirect to login
    if (response.status === 401) {
        console.log('Got 401, redirecting to login');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
    }

    return response;
};