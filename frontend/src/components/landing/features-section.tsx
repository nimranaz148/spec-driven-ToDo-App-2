'use client';

import { useEffect, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
  CheckCircle2,
  MessageSquare,
  Mic,
  BarChart3,
  Calendar,
  Zap,
  Shield,
  Bell,
} from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const features = [
  {
    icon: CheckCircle2,
    title: 'Smart Task Management',
    description:
      'Create, organize, and prioritize tasks with intelligent suggestions and automatic categorization.',
  },
  {
    icon: MessageSquare,
    title: 'AI Chat Assistant',
    description:
      'Interact with your tasks using natural language. Ask questions, get summaries, and manage tasks through conversation.',
  },
  {
    icon: Mic,
    title: 'Voice Commands',
    description:
      'Hands-free task management with advanced voice recognition. Create and complete tasks by just speaking.',
  },
  {
    icon: BarChart3,
    title: 'Beautiful Analytics',
    description:
      'Track your productivity with stunning visualizations. Understand your habits and improve over time.',
  },
  {
    icon: Calendar,
    title: 'Smart Scheduling',
    description:
      'Never miss a deadline with intelligent reminders and calendar integration across all your devices.',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description:
      'Optimized for speed with instant sync across all devices. Your tasks are always up to date.',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description:
      'Enterprise-grade security with end-to-end encryption. Your data is always protected.',
  },
  {
    icon: Bell,
    title: 'Smart Notifications',
    description:
      'Intelligent reminders that learn your patterns and notify you at the perfect time.',
  },
];

export function FeaturesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Animate cards on scroll
      gsap.fromTo(
        cardsRef.current?.children || [],
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          stagger: 0.1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: cardsRef.current,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Everything You Need to
            <span className="text-gradient-gold"> Stay Productive</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Powerful features designed to help you manage tasks effortlessly and
            achieve your goals faster than ever.
          </p>
        </div>

        {/* Features Grid */}
        <div
          ref={cardsRef}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {features.map((feature) => (
            <Card
              key={feature.title}
              className="group relative overflow-hidden border-border/50 bg-card hover:border-primary/30 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5"
            >
              <CardContent className="p-6">
                <div className="mb-4 inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-300">
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </CardContent>
              {/* Hover gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
