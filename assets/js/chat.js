/**
 * chat.js
 * Zenalyze - Chat Interface JavaScript
 * Handles AI chat, messaging, voice recording, and emoji picker
 */

class ChatInterface {
    constructor() {
        this.messageContainer = document.querySelector('.chat-messages');
        this.inputField = document.querySelector('.chat-input');
        this.sendButton = document.querySelector('.chat-send-btn');
        this.emojiButton = document.querySelector('.emoji-btn');
        this.attachmentButton = document.querySelector('.attachment-btn');
        this.voiceButton = document.querySelector('.voice-btn');
        this.suggestionChips = document.querySelectorAll('.ai-suggestion-chip');
        this.chatContacts = document.querySelectorAll('.chat-contact');
        
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.typingTimeout = null;
        this.messageQueue = [];
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.initEmojiPicker();
        this.initVoiceRecording();
        this.initDragAndDrop();
        this.scrollToBottom();
    }
    
    bindEvents() {
        // Send message on button click
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Send message on Enter (but Shift+Enter for new line)
        if (this.inputField) {
            this.inputField.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Typing indicator
            this.inputField.addEventListener('input', () => {
                this.handleTyping();
            });
        }
        
        // Suggestion chips
        this.suggestionChips.forEach(chip => {
            chip.addEventListener('click', () => {
                this.inputField.value = chip.textContent.trim();
                this.sendMessage();
            });
        });
        
        // Chat contacts
        this.chatContacts.forEach(contact => {
            contact.addEventListener('click', () => {
                this.switchChat(contact);
            });
        });
        
        // Attachment button
        if (this.attachmentButton) {
            this.attachmentButton.addEventListener('click', () => {
                this.handleAttachment();
            });
        }
        
        // Window resize
        window.addEventListener('resize', debounce(() => {
            this.adjustLayout();
        }, 250));
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.inputField.value = '';
        this.adjustTextareaHeight();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to AI
            const response = await this.getAIResponse(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add AI response
            this.addMessage(response, 'ai');
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai', true);
        }
    }
    
    addMessage(text, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'AI';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('p');
        messageText.textContent = text;
        
        const time = document.createElement('span');
        time.className = 'message-time';
        time.textContent = this.formatTime(new Date());
        
        content.appendChild(messageText);
        content.appendChild(time);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        if (isError) {
            content.style.backgroundColor = 'rgba(220, 53, 69, 0.1)';
            content.style.color = '#dc3545';
        }
        
        this.messageContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Save to localStorage
        this.saveMessage(text, sender);
    }
    
    async getAIResponse(message) {
        // Simulate AI response (replace with actual API call)
        return new Promise((resolve) => {
            setTimeout(() => {
                const responses = [
                    "I understand how you're feeling. Would you like to talk more about it?",
                    "That's a great insight. How does that make you feel?",
                    "Thank you for sharing. Remember, it's okay to feel this way.",
                    "Would you like to try a quick breathing exercise together?",
                    "I'm here to listen. What else is on your mind?",
                    "That's a positive step. How can I support you further?"
                ];
                resolve(responses[Math.floor(Math.random() * responses.length)]);
            }, 1500);
        });
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message ai typing-indicator-container';
        indicator.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = 'AI';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingDiv.appendChild(dot);
        }
        
        indicator.appendChild(avatar);
        indicator.appendChild(typingDiv);
        
        this.messageContainer.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    handleTyping() {
        // Clear previous timeout
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Send typing indicator to server (implement WebSocket here)
        
        // Set timeout to stop typing indicator
        this.typingTimeout = setTimeout(() => {
            // Stop typing indicator
        }, 1000);
    }
    
    adjustTextareaHeight() {
        if (this.inputField) {
            this.inputField.style.height = 'auto';
            this.inputField.style.height = this.inputField.scrollHeight + 'px';
        }
    }
    
    scrollToBottom() {
        if (this.messageContainer) {
            this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
        }
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    saveMessage(text, sender) {
        const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
        history.push({
            text,
            sender,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 messages
        if (history.length > 50) {
            history.shift();
        }
        
        localStorage.setItem('chatHistory', JSON.stringify(history));
    }
    
    loadChatHistory() {
        const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
        history.forEach(msg => {
            this.addMessage(msg.text, msg.sender);
        });
    }
    
    clearHistory() {
        if (confirm('Clear chat history?')) {
            localStorage.removeItem('chatHistory');
            this.messageContainer.innerHTML = '';
            this.addMessage('Chat history cleared. How can I help you today?', 'ai');
        }
    }
    
    initEmojiPicker() {
        if (!this.emojiButton) return;
        
        const emojiPicker = document.createElement('div');
        emojiPicker.className = 'emoji-picker';
        
        // Common emojis
        const emojis = ['😊', '😌', '😢', '😤', '😴', '🥰', '😎', '🤔', '🙏', '💪', '🧘', '❤️', '🌟', '🌙', '☀️', '🌈'];
        
        const grid = document.createElement('div');
        grid.className = 'emoji-grid';
        
        emojis.forEach(emoji => {
            const item = document.createElement('span');
            item.className = 'emoji-item';
            item.textContent = emoji;
            item.addEventListener('click', () => {
                this.inputField.value += emoji;
                this.emojiButton.classList.remove('active');
                emojiPicker.classList.remove('active');
            });
            grid.appendChild(item);
        });
        
        emojiPicker.appendChild(grid);
        this.emojiButton.parentNode.appendChild(emojiPicker);
        
        this.emojiButton.addEventListener('click', (e) => {
            e.stopPropagation();
            emojiPicker.classList.toggle('active');
            this.emojiButton.classList.toggle('active');
        });
        
        // Close emoji picker when clicking outside
        document.addEventListener('click', (e) => {
            if (!emojiPicker.contains(e.target) && !this.emojiButton.contains(e.target)) {
                emojiPicker.classList.remove('active');
                this.emojiButton.classList.remove('active');
            }
        });
    }
    
    initVoiceRecording() {
        if (!this.voiceButton || !navigator.mediaDevices) return;
        
        this.voiceButton.addEventListener('click', async () => {
            if (!this.isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.startRecording(stream);
                } catch (error) {
                    console.error('Microphone access denied:', error);
                    alert('Please allow microphone access to use voice recording.');
                }
            } else {
                this.stopRecording();
            }
        });
    }
    
    async startRecording(stream) {
        this.isRecording = true;
        this.voiceButton.classList.add('recording');
        
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        
        this.mediaRecorder.addEventListener('dataavailable', event => {
            this.audioChunks.push(event.data);
        });
        
        this.mediaRecorder.addEventListener('stop', () => {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            this.sendAudioMessage(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        });
        
        this.mediaRecorder.start();
        
        // Show recording UI
        this.showRecordingUI();
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.voiceButton.classList.remove('recording');
            this.hideRecordingUI();
        }
    }
    
    showRecordingUI() {
        const recordingUI = document.createElement('div');
        recordingUI.className = 'voice-recording';
        recordingUI.id = 'voice-recording-ui';
        
        recordingUI.innerHTML = `
            <div class="voice-wave">
                ${Array(20).fill().map(() => '<span></span>').join('')}
            </div>
            <div class="voice-time">00:00</div>
            <div class="voice-actions">
                <button class="voice-stop"><i class="bi bi-stop-fill"></i></button>
                <button class="voice-cancel"><i class="bi bi-x-lg"></i></button>
            </div>
        `;
        
        document.querySelector('.chat-input-area').appendChild(recordingUI);
        
        // Timer
        let seconds = 0;
        const timer = setInterval(() => {
            seconds++;
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            document.querySelector('.voice-time').textContent = 
                `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);
        
        // Stop button
        recordingUI.querySelector('.voice-stop').addEventListener('click', () => {
            clearInterval(timer);
            this.stopRecording();
        });
        
        // Cancel button
        recordingUI.querySelector('.voice-cancel').addEventListener('click', () => {
            clearInterval(timer);
            this.cancelRecording();
        });
    }
    
    hideRecordingUI() {
        const recordingUI = document.getElementById('voice-recording-ui');
        if (recordingUI) {
            recordingUI.remove();
        }
    }
    
    cancelRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.mediaRecorder = null;
            this.isRecording = false;
            this.voiceButton.classList.remove('recording');
            this.hideRecordingUI();
        }
    }
    
    async sendAudioMessage(audioBlob) {
        // Add audio message to chat
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">U</div>
            <div class="message-content">
                <div class="message-attachment">
                    <i class="bi bi-mic"></i>
                    <div class="message-attachment-info">
                        <div class="message-attachment-name">Voice Message</div>
                        <div class="message-attachment-size">${(audioBlob.size / 1024).toFixed(1)} KB</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary" onclick="this.parentElement.querySelector('audio').play()">
                        <i class="bi bi-play-fill"></i>
                    </button>
                </div>
                <audio src="${URL.createObjectURL(audioBlob)}" style="display: none;"></audio>
                <span class="message-time">${this.formatTime(new Date())}</span>
            </div>
        `;
        
        this.messageContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Process voice message with AI
        this.showTypingIndicator();
        setTimeout(() => {
            this.hideTypingIndicator();
            this.addMessage("I've received your voice message. How can I help you?", 'ai');
        }, 2000);
    }
    
    handleAttachment() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,.pdf,.doc,.docx,.txt';
        input.multiple = true;
        
        input.addEventListener('change', () => {
            Array.from(input.files).forEach(file => {
                this.sendFileMessage(file);
            });
        });
        
        input.click();
    }
    
    async sendFileMessage(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user';
            
            let attachmentHtml = '';
            
            if (file.type.startsWith('image/')) {
                attachmentHtml = `
                    <img src="${e.target.result}" 
                         alt="${file.name}" 
                         style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                `;
            } else {
                attachmentHtml = `
                    <div class="message-attachment">
                        <i class="bi ${this.getFileIcon(file.type)}"></i>
                        <div class="message-attachment-info">
                            <div class="message-attachment-name">${file.name}</div>
                            <div class="message-attachment-size">${(file.size / 1024).toFixed(1)} KB</div>
                        </div>
                    </div>
                `;
            }
            
            messageDiv.innerHTML = `
                <div class="message-avatar">U</div>
                <div class="message-content">
                    ${attachmentHtml}
                    <span class="message-time">${this.formatTime(new Date())}</span>
                </div>
            `;
            
            this.messageContainer.appendChild(messageDiv);
            this.scrollToBottom();
        };
        
        if (file.type.startsWith('image/')) {
            reader.readAsDataURL(file);
        } else {
            reader.readAsText(file);
        }
    }
    
    getFileIcon(mimeType) {
        if (mimeType.startsWith('image/')) return 'bi-file-image';
        if (mimeType.includes('pdf')) return 'bi-file-pdf';
        if (mimeType.includes('word')) return 'bi-file-word';
        if (mimeType.includes('text')) return 'bi-file-text';
        return 'bi-file';
    }
    
    initDragAndDrop() {
        const dropZone = document.querySelector('.chat-input-area');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            Array.from(files).forEach(file => this.sendFileMessage(file));
        });
    }
    
    switchChat(contactElement) {
        // Remove active class from all contacts
        this.chatContacts.forEach(c => c.classList.remove('active'));
        
        // Add active class to selected contact
        contactElement.classList.add('active');
        
        // Load chat history for this contact
        const contactName = contactElement.querySelector('.chat-contact-name').textContent;
        this.loadContactHistory(contactName);
    }
    
    loadContactHistory(contactName) {
        // Clear current messages
        this.messageContainer.innerHTML = '';
        
        // Add welcome message
        this.addMessage(`Chatting with ${contactName}`, 'ai');
        
        // Load history from localStorage
        const history = JSON.parse(localStorage.getItem(`chat_${contactName}`) || '[]');
        history.forEach(msg => {
            this.addMessage(msg.text, msg.sender);
        });
    }
    
    adjustLayout() {
        // Adjust chat layout on window resize
        if (window.innerWidth <= 768) {
            // Mobile layout adjustments
            document.querySelector('.chat-sidebar')?.classList.add('collapsed');
        } else {
            document.querySelector('.chat-sidebar')?.classList.remove('collapsed');
        }
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.chat-container')) {
        window.chatInterface = new ChatInterface();
    }
});