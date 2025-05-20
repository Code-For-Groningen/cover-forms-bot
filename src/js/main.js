const { Client, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

const client = new Client();
const tempCommandFile = `/tmp/wapp_command_${process.pid}.txt`;

// Create the pipe if it doesn't exist
try {
    if (!fs.existsSync(tempCommandFile)) {
        fs.writeFileSync(tempCommandFile, '', { mode: 0o600 });
        console.log(`WAPP: Created command pipe at: ${tempCommandFile}`);
    }
} catch (error) {
    console.error('WAPP: Error creating command pipe:', error);
}

client.on('qr', (qr) => {
    // Generate and scan this code with your phone
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('WAPP: Client is ready!');
    console.log(`WAPP: Watching for commands in: ${tempCommandFile}`);
    
    // Watch the command file for changes
    fs.watchFile(tempCommandFile, { interval: 1000 }, async () => {
        try {
            const content = fs.readFileSync(tempCommandFile, 'utf8').trim();
            
            if (!content) return;
            
            console.log(`WAPP: Received command: ${content}`);
            
            // Parse input using regex to handle quotes properly
            const match = content.match(/"([^"]+)"\s+([^\s"]+)\s+"([^"]+)"/);
            
            const [, channelName, imagePath, caption] = match;
            
            // Check if file exists
            if (!fs.existsSync(imagePath)) {
                console.log(`WAPP: Image file not found: ${imagePath}`);
                fs.writeFileSync(tempCommandFile, '', 'utf8');
                return;
            }
            
            // Get all chats
            const chats = await client.getChats();
            
            // Find the group chat with the specified name
            const targetChat = chats.find(chat => chat.name === channelName);
            
            if (targetChat) {
                const media = MessageMedia.fromFilePath(imagePath);
                await client.sendMessage(targetChat.id._serialized, media, { caption });
                console.log(`WAPP: ✅`);
            } else {
                console.log(`WAPP: Channel "${channelName}" not found`);
            }
            
            // Clear the command file after processing
            fs.writeFileSync(tempCommandFile, '', 'utf8');
        } catch (error) {
            console.error('WAPP: Error!', error.message);
            // Clear the command file on error
            fs.writeFileSync(tempCommandFile, '', 'utf8');
        }
    });
});

client.on('message', msg => {
    if (msg.body == '!ping') {
        msg.reply('pong');
    }
});

client.initialize();

// Clean up on exit
process.on('SIGINT', () => {
    fs.unwatchFile(tempCommandFile);
    try {
        fs.unlinkSync(tempCommandFile);
        console.log(`Removed command pipe: ${tempCommandFile}`);
    } catch (error) {
        console.error('Error cleaning up:', error);
    }
    process.exit();
});