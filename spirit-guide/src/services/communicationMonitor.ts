interface CommunicationPattern {
    type: 'text' | 'call';
    content?: string;
    duration?: number;
    timestamp: Date;
    indicators: string[];
    intensity: number;
}

interface GuidanceResponse {
    message: string;
    suggestion: string;
    practicalSteps: string[];
    spiritualPrinciple: string;
}

export class CommunicationMonitor {
    private patterns: CommunicationPattern[] = [];
    private onGuidanceNeeded: (guidance: GuidanceResponse) => void;

    constructor(onGuidanceNeeded: (guidance: GuidanceResponse) => void) {
        this.onGuidanceNeeded = onGuidanceNeeded;
    }

    analyzeMessage(content: string, type: 'text' | 'call', duration?: number) {
        const pattern: CommunicationPattern = {
            type,
            content,
            duration,
            timestamp: new Date(),
            indicators: [],
            intensity: 0
        };

        // Analyze for negative patterns
        const negativePatterns = this.detectNegativePatterns(content);
        pattern.indicators = negativePatterns;
        pattern.intensity = this.calculateIntensity(negativePatterns);

        this.patterns.push(pattern);
        this.checkForPatterns();
    }

    private detectNegativePatterns(content: string): string[] {
        const indicators: string[] = [];
        const lowerContent = content.toLowerCase();

        // Communication patterns that might indicate spiritual challenges
        const patterns = {
            judgment: ['they always', 'never', 'hate', 'stupid', 'wrong'],
            separation: ['alone', 'nobody', 'by myself', 'abandoned'],
            fear: ['worried', 'scared', 'afraid', 'terrified'],
            attachment: ['need to have', 'can\'t live without', 'must get'],
            ego: ['better than', 'deserve', 'entitled', 'should have']
        };

        Object.entries(patterns).forEach(([category, keywords]) => {
            if (keywords.some(word => lowerContent.includes(word))) {
                indicators.push(category);
            }
        });

        return indicators;
    }

    private calculateIntensity(indicators: string[]): number {
        // Base intensity on number of different types of indicators
        return Math.min(10, indicators.length * 2);
    }

    private checkForPatterns() {
        const recentPatterns = this.patterns.slice(-5);
        const totalIntensity = recentPatterns.reduce((sum, p) => sum + p.intensity, 0);
        const averageIntensity = totalIntensity / recentPatterns.length;

        if (averageIntensity > 6) {
            this.provideGuidance(recentPatterns);
        }
    }

    private provideGuidance(patterns: CommunicationPattern[]) {
        // Identify primary challenge from patterns
        const allIndicators = patterns.flatMap(p => p.indicators);
        const primaryChallenge = this.getMostFrequent(allIndicators);

        const guidance = this.generateGuidance(primaryChallenge);
        this.onGuidanceNeeded(guidance);
    }

    private generateGuidance(challenge: string): GuidanceResponse {
        const guidanceMap: Record<string, GuidanceResponse> = {
            judgment: {
                message: "Your communications show a pattern of judgment.",
                suggestion: "Consider that each person is on their own spiritual journey.",
                practicalSteps: [
                    "Before responding, pause and ask 'What might I not understand?'",
                    "Look for one positive quality in the situation or person",
                    "Replace 'they always/never' with specific observations"
                ],
                spiritualPrinciple: "Unity and Understanding"
            },
            separation: {
                message: "You seem to be feeling disconnected or isolated.",
                suggestion: "Remember that you are always connected to the Higher Spirit.",
                practicalSteps: [
                    "Reach out to one person with pure intentions",
                    "Spend time in prayer or meditation",
                    "Look for ways to serve others"
                ],
                spiritualPrinciple: "Divine Connection"
            },
            fear: {
                message: "Fear appears to be influencing your communications.",
                suggestion: "Trust in the divine plan and your spiritual guidance.",
                practicalSteps: [
                    "Write down your fears and examine their source",
                    "Practice gratitude for what is working",
                    "Take one small step forward with faith"
                ],
                spiritualPrinciple: "Faith over Fear"
            },
            attachment: {
                message: "You may be holding too tightly to outcomes or possessions.",
                suggestion: "Practice letting go and trusting in divine timing.",
                practicalSteps: [
                    "Identify what you can and cannot control",
                    "Practice generosity in small ways",
                    "Focus on being rather than having"
                ],
                spiritualPrinciple: "Divine Providence"
            },
            ego: {
                message: "Your ego might be creating separation from others.",
                suggestion: "Return to humility and openness to learning.",
                practicalSteps: [
                    "Look for lessons in challenging situations",
                    "Practice listening more than speaking",
                    "Ask 'How can I serve?' instead of 'What should I get?'"
                ],
                spiritualPrinciple: "Humility and Growth"
            }
        };

        return guidanceMap[challenge] || {
            message: "Take a moment to reflect on your communications.",
            suggestion: "Consider how you can bring more light and unity to your interactions.",
            practicalSteps: ["Pause", "Reflect", "Respond with love"],
            spiritualPrinciple: "Mindful Communication"
        };
    }

    private getMostFrequent(arr: string[]): string {
        return arr.sort((a, b) =>
            arr.filter(v => v === a).length - arr.filter(v => v === b).length
        ).pop() || '';
    }

    getRecentPatterns(days: number = 7): CommunicationPattern[] {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        return this.patterns.filter(p => p.timestamp >= cutoff);
    }

    clearOldPatterns(days: number = 30) {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        this.patterns = this.patterns.filter(p => p.timestamp >= cutoff);
    }
} 