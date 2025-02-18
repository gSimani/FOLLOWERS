import annyang from 'annyang';

interface StressPattern {
    keywords: string[];
    intensity: number;
    category: 'anger' | 'anxiety' | 'frustration' | 'fear' | 'overwhelm';
}

const stressPatterns: StressPattern[] = [
    {
        keywords: ['can\'t take it', 'too much', 'overwhelmed', 'stressed'],
        intensity: 8,
        category: 'overwhelm'
    },
    {
        keywords: ['angry', 'furious', 'mad', 'upset'],
        intensity: 7,
        category: 'anger'
    },
    {
        keywords: ['worried', 'anxious', 'nervous', 'scared'],
        intensity: 6,
        category: 'anxiety'
    }
];

export class VoiceDetectionService {
    private isListening: boolean = false;
    private onStressDetected: (pattern: StressPattern) => void;
    private voicePatterns: Map<string, number> = new Map(); // Track frequency of patterns

    constructor(onStressDetected: (pattern: StressPattern) => void) {
        this.onStressDetected = onStressDetected;
    }

    startListening() {
        if (!annyang) {
            console.error('Speech recognition not supported');
            return;
        }

        const commands = {
            '*text': (text: string) => this.analyzeText(text)
        };

        annyang.addCommands(commands);
        annyang.start({ autoRestart: true, continuous: true });
        this.isListening = true;

        // Monitor voice tone and speed
        annyang.addCallback('result', (phrases: string[]) => {
            this.analyzeTone(phrases[0]);
        });
    }

    stopListening() {
        if (annyang) {
            annyang.abort();
            this.isListening = false;
        }
    }

    private analyzeText(text: string) {
        // Convert to lowercase for better matching
        const lowerText = text.toLowerCase();

        // Check for stress patterns
        stressPatterns.forEach(pattern => {
            const matches = pattern.keywords.some(keyword => 
                lowerText.includes(keyword.toLowerCase())
            );

            if (matches) {
                this.incrementPattern(pattern.category);
                this.onStressDetected(pattern);
            }
        });
    }

    private analyzeTone(text: string) {
        // Basic tone analysis based on punctuation and capitalization
        const exclamationCount = (text.match(/!/g) || []).length;
        const capsCount = (text.match(/[A-Z]/g) || []).length;
        const wordCount = text.split(' ').length;

        if (exclamationCount > 2 || (capsCount / wordCount) > 0.5) {
            this.onStressDetected({
                keywords: ['elevated tone'],
                intensity: 7,
                category: 'anger'
            });
        }
    }

    private incrementPattern(category: string) {
        const current = this.voicePatterns.get(category) || 0;
        this.voicePatterns.set(category, current + 1);

        // Check for repeated patterns that might indicate deeper issues
        if (current + 1 >= 3) {
            this.suggestSpiritualGuidance(category);
        }
    }

    private suggestSpiritualGuidance(category: string) {
        const guidanceMap = {
            anger: "Consider what this anger is teaching you about your expectations and attachments.",
            anxiety: "This moment of worry is an invitation to deepen your trust in the Higher Spirit.",
            frustration: "What lesson might be hidden in this challenge?",
            fear: "Fear often points to where we need to grow in faith and understanding.",
            overwhelm: "This feeling of overwhelm is asking you to reconnect with your spiritual center."
        };

        // Trigger guidance callback with appropriate message
        if (guidanceMap[category]) {
            this.onStressDetected({
                keywords: ['guidance needed'],
                intensity: 9,
                category: category as StressPattern['category']
            });
        }
    }

    getStressPatternHistory(): Map<string, number> {
        return new Map(this.voicePatterns);
    }
} 