/**
 * Soul Chat Robot - Web界面前端脚本
 */

// 当文档加载完成后执行初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM已加载，初始化应用...');
    initApp();
});

// 应用初始化
function initApp() {
    // 获取DOM元素
    const elements = {
        // 设备控制
        deviceSelect: document.getElementById('device-select'),
        refreshDevices: document.getElementById('refresh-devices'),
        connectDevice: document.getElementById('connect-device'),
        connectionStatus: document.getElementById('connection-status'),
        deviceInfo: document.getElementById('device-info'),
        
        // 截图
        takeScreenshot: document.getElementById('take-screenshot'),
        screenshotImg: document.getElementById('screenshot-img'),
        noScreenshot: document.getElementById('no-screenshot'),
        screenOverlay: document.getElementById('screen-overlay'),
        tapCoordinates: document.getElementById('tap-coordinates'),
        enableTap: document.getElementById('enable-tap'),
        
        // 按键
        btnBack: document.getElementById('btn-back'),
        btnHome: document.getElementById('btn-home'),
        
        // 任务管理
        btnNewTask: document.getElementById('btn-new-task'),
        btnCreateFirstTask: document.getElementById('btn-create-first-task'),
        btnSaveTasks: document.getElementById('btn-save-tasks'),
        btnLoadTasks: document.getElementById('btn-load-tasks')
    };
    
    // 检查关键元素是否存在
    for (const key in elements) {
        if (elements[key] === null) {
            console.error(`找不到元素: ${key}`);
        }
    }
    
    // 绑定事件处理程序
    if (elements.refreshDevices) {
        elements.refreshDevices.addEventListener('click', function() {
            console.log('刷新设备列表');
            fetchDevices();
        });
    }
    
    if (elements.connectDevice) {
        elements.connectDevice.addEventListener('click', function() {
            console.log('连接设备');
            connectSelectedDevice();
        });
    }
    
    if (elements.takeScreenshot) {
        elements.takeScreenshot.addEventListener('click', function() {
            console.log('获取截图');
            takeScreenshot();
        });
    }
    
    if (elements.btnBack) {
        elements.btnBack.addEventListener('click', function() {
            console.log('按下返回键');
            pressKey(4);
        });
    }
    
    if (elements.btnHome) {
        elements.btnHome.addEventListener('click', function() {
            console.log('按下Home键');
            pressKey(3);
        });
    }
    
    if (elements.enableTap) {
        elements.enableTap.addEventListener('change', function(event) {
            console.log('切换点击功能:', event.target.checked);
            toggleTapFeature(event.target.checked);
        });
    }
    
    if (elements.screenOverlay) {
        elements.screenOverlay.addEventListener('click', function(event) {
            handleScreenTap(event);
        });
    }
    
    // 初始化
    fetchDevices();
    
    console.log('应用初始化完成');
}

// 获取设备列表
function fetchDevices() {
    fetch('/devices')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDeviceList(data.devices, data.connected_device);
            } else {
                showError('获取设备列表失败');
            }
        })
        .catch(error => {
            console.error('获取设备列表出错:', error);
            showError('网络错误，无法获取设备列表');
        });
}

// 更新设备列表
function updateDeviceList(devices, connectedDevice) {
    const deviceSelect = document.getElementById('device-select');
    if (!deviceSelect) return;
    
    // 清空设备列表
    deviceSelect.innerHTML = '<option value="">-- 选择设备 --</option>';
    
    // 添加设备选项
    if (devices && devices.length > 0) {
        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.id;
            option.textContent = `${device.id} (${device.model || '未知型号'})`;
            
            // 如果是当前连接的设备，则选中
            if (device.id === connectedDevice) {
                option.selected = true;
                updateConnectionStatus(true, device);
            }
            
            deviceSelect.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.value = "";
        option.textContent = "未找到设备";
        option.disabled = true;
        deviceSelect.appendChild(option);
    }
}

// 连接选中的设备
function connectSelectedDevice() {
    const deviceSelect = document.getElementById('device-select');
    if (!deviceSelect) return;
    
    const deviceId = deviceSelect.value;
    if (!deviceId) {
        showError('请选择一个设备');
        return;
    }
    
    // 显示连接中状态
    updateConnectionStatus('connecting');
    
    // 发送连接请求
    fetch('/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ device_id: deviceId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateConnectionStatus(true, { id: deviceId });
            enableDeviceControls(true);
        } else {
            updateConnectionStatus(false);
            showError(data.message || '连接设备失败');
        }
    })
    .catch(error => {
        console.error('连接设备出错:', error);
        updateConnectionStatus(false);
        showError('网络错误，无法连接设备');
    });
}

// 更新连接状态
function updateConnectionStatus(status, device) {
    const connectionStatus = document.getElementById('connection-status');
    const deviceInfo = document.getElementById('device-info');
    
    if (!connectionStatus || !deviceInfo) return;
    
    if (status === 'connecting') {
        connectionStatus.className = 'badge bg-warning';
        connectionStatus.textContent = '连接中...';
        deviceInfo.textContent = '';
        return;
    }
    
    if (status) {
        connectionStatus.className = 'badge bg-success';
        connectionStatus.textContent = '已连接';
        
        if (device) {
            deviceInfo.textContent = device.id;
        }
    } else {
        connectionStatus.className = 'badge bg-danger';
        connectionStatus.textContent = '未连接';
        deviceInfo.textContent = '';
    }
}

// 启用/禁用设备控制按钮
function enableDeviceControls(enabled) {
    const btnTakeScreenshot = document.getElementById('take-screenshot');
    const btnBack = document.getElementById('btn-back');
    const btnHome = document.getElementById('btn-home');
    const enableTap = document.getElementById('enable-tap');
    
    if (btnTakeScreenshot) btnTakeScreenshot.disabled = !enabled;
    if (btnBack) btnBack.disabled = !enabled;
    if (btnHome) btnHome.disabled = !enabled;
    if (enableTap) enableTap.disabled = !enabled;
}

// 获取屏幕截图
function takeScreenshot() {
    const screenshotImg = document.getElementById('screenshot-img');
    const noScreenshot = document.getElementById('no-screenshot');
    const screenResolution = document.getElementById('screen-resolution');
    const screenshotTime = document.getElementById('screenshot-time');
    
    if (!screenshotImg || !noScreenshot) return;
    
    // 显示加载状态
    if (screenshotImg.classList.contains('d-none')) {
        screenshotImg.classList.remove('d-none');
    }
    noScreenshot.classList.add('d-none');
    screenshotImg.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==';
    
    fetch('/screenshot')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 显示截图
                screenshotImg.src = 'data:image/png;base64,' + data.image;
                
                // 显示截图时间
                if (screenshotTime) {
                    const timestamp = new Date(data.timestamp);
                    screenshotTime.textContent = timestamp.toLocaleTimeString();
                }
                
                // 显示分辨率
                screenshotImg.onload = function() {
                    if (screenResolution) {
                        screenResolution.textContent = `${this.naturalWidth} × ${this.naturalHeight}`;
                    }
                };
            } else {
                showError(data.message || '获取截图失败');
                
                // 恢复无截图状态
                screenshotImg.classList.add('d-none');
                noScreenshot.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('获取截图出错:', error);
            showError('网络错误，无法获取截图');
            
            // 恢复无截图状态
            screenshotImg.classList.add('d-none');
            noScreenshot.classList.remove('d-none');
        });
}

// 按下按键
function pressKey(keyCode) {
    fetch('/key', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key_code: keyCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status !== 'success') {
            showError(data.message || '按键操作失败');
        }
    })
    .catch(error => {
        console.error('按键操作出错:', error);
        showError('网络错误，无法执行按键操作');
    });
}

// 切换点击功能
function toggleTapFeature(enabled) {
    const screenOverlay = document.getElementById('screen-overlay');
    
    if (!screenOverlay) return;
    
    if (enabled) {
        screenOverlay.classList.remove('d-none');
    } else {
        screenOverlay.classList.add('d-none');
    }
}

// 处理屏幕点击
function handleScreenTap(event) {
    const screenOverlay = document.getElementById('screen-overlay');
    const screenshotImg = document.getElementById('screenshot-img');
    const enableTap = document.getElementById('enable-tap');
    const tapCoordinates = document.getElementById('tap-coordinates');
    
    if (!screenOverlay || !screenshotImg || !enableTap || !enableTap.checked) return;
    
    const rect = screenOverlay.getBoundingClientRect();
    const scaleX = screenshotImg.naturalWidth / rect.width;
    const scaleY = screenshotImg.naturalHeight / rect.height;
    
    const x = Math.round((event.clientX - rect.left) * scaleX);
    const y = Math.round((event.clientY - rect.top) * scaleY);
    
    // 显示点击位置
    if (tapCoordinates) {
        tapCoordinates.textContent = `点击坐标: (${x}, ${y})`;
    }
    
    // 显示点击动画
    const tapIndicator = document.getElementById('tap-indicator');
    if (tapIndicator) {
        tapIndicator.style.left = (event.clientX - rect.left) + 'px';
        tapIndicator.style.top = (event.clientY - rect.top) + 'px';
        tapIndicator.classList.remove('d-none');
        
        setTimeout(() => {
            tapIndicator.classList.add('d-none');
        }, 500);
    }
    
    // 发送点击请求
    fetch('/tap', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status !== 'success') {
            showError(data.message || '点击操作失败');
        }
    })
    .catch(error => {
        console.error('点击操作出错:', error);
        showError('网络错误，无法执行点击操作');
    });
}

// 显示错误消息
function showError(message) {
    console.error(message);
    alert(message);
}
