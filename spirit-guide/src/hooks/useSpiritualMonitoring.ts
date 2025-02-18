import { useState, useEffect, useCallback } from 'react';
import { VoiceDetectionService } from '../services/voiceDetection';
import { CommunicationMonitor } from '../services/communicationMonitor';

interface SpiritualInsight {
    timestamp: Date;
    type: 'voice' | 'communication';
    message: string;
    guidance: string;
    steps: string[];
    principle: string;
}

export function useSpiritualMonitoring() {
    const [insights, setInsights] = useState<SpiritualInsight[]>([]);
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [voiceService, setVoiceService] = useState<VoiceDetectionService | null>(null);
    const [commMonitor, setCommMonitor] = useState<CommunicationMonitor | null>(null);

    // Initialize services
    useEffect(() => {
        const handleStressDetected = (pattern: any) => {
            const insight: SpiritualInsight = {
                timestamp: new Date(),
                type: 'voice',
                message: `Detected ${pattern.category} pattern in voice`,
                guidance: getGuidanceForPattern(pattern.category),
                steps: getStepsForPattern(pattern.category),
                principle: getPrincipleForPattern(pattern.category)
            };
            setInsights(prev => [...prev, insight]);
        };

        const handleGuidanceNeeded = (guidance: any) => {
            const insight: SpiritualInsight = {
                timestamp: new Date(),
                type: 'communication',
                message: guidance.message,
                guidance: guidance.suggestion,
                steps: guidance.practicalSteps,
                principle: guidance.spiritualPrinciple
            };
            setInsights(prev => [...prev, insight]);
        };

        const voice = new VoiceDetectionService(handleStressDetected);
        const comm = new CommunicationMonitor(handleGuidanceNeeded);

        setVoiceService(voice);
        setCommMonitor(comm);

        return () => {
            voice.stopListening();
        };
    }, []);

    // Start monitoring
    const startMonitoring = useCallback(() => {
        if (voiceService) {
            voiceService.startListening();
        }
        setIsMonitoring(true);
    }, [voiceService]);

    // Stop monitoring
    const stopMonitoring = useCallback(() => {
        if (voiceService) {
            voiceService.stopListening();
        }
        setIsMonitoring(false);
    }, [voiceService]);

    // Analyze communication
    const analyzeCommunication = useCallback((content: string, type: 'text' | 'call', duration?: number) => {
        if (commMonitor) {
            commMonitor.analyzeMessage(content, type, duration);
        }
    }, [commMonitor]);

    // Get recent insights
    const getRecentInsights = useCallback((days: number = 7) => {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        return insights.filter(insight => insight.timestamp >= cutoff);
    }, [insights]);

    // Helper functions for spiritual guidance
    function getGuidanceForPattern(category: string): string {
        const guidance = {
            anger: "This anger is a teacher. What is it showing you about your expectations?",
            anxiety: "Anxiety often arises when we forget our connection to the Divine.",
            frustration: "Each obstacle is an opportunity for spiritual growth.",
            fear: "Fear is an invitation to deepen your faith.",
            overwhelm: "When overwhelmed, return to your spiritual center."
        };
        return guidance[category] || "Take this moment to connect with your higher purpose.";
    }

    function getStepsForPattern(category: string): string[] {
        const steps = {
            anger: [
                "Take three deep breaths",
                "Ask: What expectation am I holding?",
                "Find one thing to be grateful for"
            ],
            anxiety: [
                "Ground yourself in the present moment",
                "Recall a time you felt Divine support",
                "Take one small step forward"
            ],
            frustration: [
                "Pause and observe without judgment",
                "Look for the lesson or growth opportunity",
                "Choose a response aligned with your values"
            ],
            fear: [
                "Acknowledge the fear without judgment",
                "Connect with your spiritual practice",
                "Take action from a place of faith"
            ],
            overwhelm: [
                "Create a moment of stillness",
                "Return to your spiritual practices",
                "Focus on one thing at a time"
            ]
        };
        return steps[category] || ["Pause", "Reflect", "Choose consciously"];
    }

    function getPrincipleForPattern(category: string): string {
        const principles = {
            anger: "Divine Patience",
            anxiety: "Trust in Higher Power",
            frustration: "Growth Through Challenges",
            fear: "Faith Over Fear",
            overwhelm: "Divine Order"
        };
        return principles[category] || "Spiritual Awareness";
    }

    return {
        isMonitoring,
        startMonitoring,
        stopMonitoring,
        analyzeCommunication,
        insights,
        getRecentInsights
    };
} 