# Forge API Tool - Bootstrap Dashboard

A modern, responsive web interface for the Forge API Tool built with **Flask** and **Bootstrap 5**.

## 🚀 Features

### Modern UI/UX
- **Bootstrap 5** - Latest responsive framework
- **Bootstrap Icons** - Beautiful, consistent iconography
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark/Light Theme Support** - Built-in theme switching
- **Smooth Animations** - CSS transitions and micro-interactions

### Real-time Functionality
- **Socket.IO Integration** - Real-time updates and notifications
- **Live Progress Tracking** - Real-time generation progress
- **System Status Monitoring** - Live system health indicators
- **Queue Management** - Real-time job queue updates

### Advanced Components
- **Modal System** - Rich modal dialogs for all interactions
- **Toast Notifications** - Non-intrusive status messages
- **Progress Bars** - Animated progress indicators
- **Data Tables** - Sortable, filterable data displays
- **File Browser** - Advanced output file management

## 📁 File Structure

```
web_dashboard/
├── app_bootstrap.py              # Main Flask application
├── run_bootstrap.py              # Startup script
├── templates/
│   ├── dashboard_bootstrap.html  # Main dashboard template
│   └── modals/                   # Modal templates
│       ├── settings_modal.html
│       ├── batch_modal.html
│       ├── status_modal.html
│       ├── template_modal.html
│       ├── outputs_modal.html
│       └── analysis_modal.html
├── static/
│   └── js/
│       └── dashboard_bootstrap.js # Main JavaScript
└── BOOTSTRAP_README.md           # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Flask
- Flask-SocketIO

### Setup
1. **Install Dependencies:**
   ```bash
   pip install flask flask-socketio
   ```

2. **Navigate to Dashboard:**
   ```bash
   cd web_dashboard
   ```

3. **Run the Application:**
   ```bash
   python run_bootstrap.py
   ```

4. **Access Dashboard:**
   Open your browser and go to: `http://localhost:5000`

## 🎨 UI Components

### Navigation
- **Responsive Navbar** - Collapsible on mobile
- **Status Indicators** - Real-time system status
- **Quick Actions** - Settings, status, refresh buttons

### Sidebar
- **Template Cards** - Interactive template selection
- **Hover Effects** - Smooth card animations
- **Action Buttons** - Generate, batch, folder access

### Main Content
- **Progress Section** - Real-time generation progress
- **Generation Form** - Comprehensive settings form
- **Output Gallery** - Image preview and management

### Modals
- **Settings Modal** - Tabbed configuration interface
- **Batch Modal** - Advanced batch generation
- **Status Modal** - System monitoring dashboard
- **Template Modal** - Template creation/editing
- **Outputs Modal** - File browser with filters
- **Analysis Modal** - Image analysis results

## 🔧 Configuration

### Bootstrap Customization
The dashboard uses Bootstrap 5 with custom CSS variables:

```css
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
    --success-color: #198754;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #0dcaf0;
}
```

### Responsive Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 992px
- **Desktop:** > 992px

## 📱 Mobile Support

The dashboard is fully responsive and optimized for mobile devices:

- **Touch-friendly** buttons and controls
- **Collapsible** sidebar on mobile
- **Optimized** layouts for small screens
- **Gesture support** for common actions

## ⚡ Performance Features

### Optimizations
- **Lazy Loading** - Images and content loaded on demand
- **Debounced Search** - Efficient search with delays
- **Pagination** - Large datasets handled efficiently
- **Caching** - Browser caching for static assets

### Real-time Updates
- **WebSocket Connection** - Low-latency updates
- **Event-driven** architecture
- **Automatic Reconnection** - Handles connection drops

## 🎯 Key Features

### Template Management
- **Visual Template Cards** - Easy template selection
- **Template Editor** - Full-featured template creation
- **Template Testing** - Test templates before saving
- **Template Import/Export** - Share templates easily

### Generation Control
- **Single Generation** - Quick single image generation
- **Batch Generation** - Multiple images with preview
- **Progress Tracking** - Real-time generation progress
- **Queue Management** - Job queue with priorities

### Output Management
- **File Browser** - Advanced file management
- **Image Preview** - Thumbnail previews
- **Search & Filter** - Find files quickly
- **Bulk Operations** - Multiple file operations

### System Monitoring
- **Health Dashboard** - System status overview
- **Performance Metrics** - Real-time performance data
- **Log Viewer** - System logs with filtering
- **Queue Status** - Job queue monitoring

## 🔌 API Integration

The dashboard integrates with the Forge API Tool's core functionality:

- **Configuration Management** - Load/save configurations
- **Image Generation** - Single and batch generation
- **Output Management** - File operations
- **System Monitoring** - Status and health checks

## 🎨 Customization

### Themes
You can easily customize the appearance by modifying the CSS variables in the main template.

### Components
All components are modular and can be customized or extended as needed.

### JavaScript
The dashboard uses modern JavaScript with ES6+ features and is fully modular.

## 🚀 Getting Started

1. **Start the Dashboard:**
   ```bash
   python run_bootstrap.py
   ```

2. **Load Templates:**
   - Add configuration files to the `configs/` directory
   - Templates will automatically appear in the sidebar

3. **Generate Images:**
   - Select a template
   - Enter your prompt
   - Click "Generate Image"

4. **Monitor Progress:**
   - Watch real-time progress updates
   - View system status
   - Check the job queue

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't start:**
- Check if Flask and Flask-SocketIO are installed
- Ensure you're in the correct directory
- Check for port conflicts

**Templates not loading:**
- Verify configuration files are in the `configs/` directory
- Check file permissions
- Look for JSON syntax errors

**Real-time updates not working:**
- Check browser console for WebSocket errors
- Ensure no firewall is blocking WebSocket connections
- Try refreshing the page

### Debug Mode
Enable debug mode in the settings modal for detailed logging and error information.

## 📈 Future Enhancements

- **Dark Mode Toggle** - User preference for dark/light themes
- **Advanced Analytics** - Detailed generation statistics
- **Plugin System** - Extensible functionality
- **Multi-language Support** - Internationalization
- **Advanced Filtering** - More sophisticated search options

## 🤝 Contributing

The Bootstrap dashboard is designed to be easily extensible. Key areas for contribution:

- **UI Components** - New Bootstrap components
- **JavaScript Modules** - Additional functionality
- **CSS Styling** - Theme improvements
- **Documentation** - Better user guides

## 📄 License

This dashboard is part of the Forge API Tool project and follows the same licensing terms.

---

**Enjoy using the modern Bootstrap dashboard! 🎉** 