const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

class AdminService {
  async getDashboard(token) {
    const response = await fetch(`${API_BASE_URL}/api/admin/dashboard`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch dashboard data');
    }
    
    return await response.json();
  }

  async getUsers(token) {
    const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    
    return await response.json();
  }

  async updateUserRole(userId, role, token) {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/role`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ role })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to update user role');
    }
    
    return data;
  }

  async getEnrollments(token) {
    const response = await fetch(`${API_BASE_URL}/api/admin/enrollments`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch enrollments');
    }
    
    return await response.json();
  }
}

export const adminService = new AdminService();