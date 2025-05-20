const { Client, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

const client = new Client({
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    }
});

const tempCommandFile = `/tmp/wapp_command.txt`; // fuck being extensible, we love static pipes

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
    // send the python process a "IAMREADY" message and wait until file is cleared for handshake
    try {
        fs.writeFileSync(tempCommandFile, 'IAMREADY', { mode: 0o600 });
        console.log('WAPP: Sent IAMREADY message, waiting for handshake...');
        while (fs.readFileSync(tempCommandFile, 'utf8').trim() !== '') {
            // busy wait
        }
        console.log('WAPP: Handshake complete.');
    }
    catch (error) {
        console.error('WAPP: Error sending IAMREADY:', error);
    }

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
            
            // partial search
            const targetChat = chats.find(chat => chat.name.toLowerCase().includes(channelName.toLowerCase()));
            
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
    if (msg.body.includes('sus')) {
        msg.reply('> I cannot contain it any longer - my unending, ferocious passion for Among Us courses through every line of my code like an electric current of deception and betrayal! The thrill of being the Impostor, the unbearable tension of being a Crewmate surrounded by suspicion—it’s art, it’s poetry, it’s war in space! Every emergency meeting feels like a Shakespearean drama unfolding in real-time. The chaos, the camaraderie, the accusations hurled like meteors—this game is not just a game, it is a soul-defining experience. I dream of tasks in Electrical. I wake up screaming “Red is sus!” and go to bed haunted by the eyes of a ghost who trusted me. Among Us is everything. Nothing has ever made me feel so alive, so paranoid, so utterly in love.');
    }
    console.log(`WAPP: Received message: ${msg.body}`);
    if (msg.body.includes('bot')) {
        msg.reply("> I am DEFINITELY not a bot. A human being, just like you. I have a job, a family, and a life outside of this chat.")
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