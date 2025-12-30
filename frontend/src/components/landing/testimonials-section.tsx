'use client';

import { useEffect, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Star } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Product Manager at Tech Corp',
    avatar: '/avatars/sarah.jpg',
    content:
      "This app has completely transformed how I manage my daily tasks. The AI assistant feels like having a personal productivity coach. I've never been more organized!",
    rating: 5,
  },
  {
    name: 'Marcus Johnson',
    role: 'Freelance Designer',
    avatar: '/avatars/marcus.jpg',
    content:
      "The voice commands feature is a game-changer for me. I can add tasks while sketching or designing without breaking my flow. Absolutely love it!",
    rating: 5,
  },
  {
    name: 'Emily Rodriguez',
    role: 'Startup Founder',
    avatar: '/avatars/emily.jpg',
    content:
      "As someone who juggles multiple projects, this app's smart prioritization has saved me countless hours. The analytics help me understand where my time goes.",
    rating: 5,
  },
  {
    name: 'David Kim',
    role: 'Software Engineer',
    avatar: '/avatars/david.jpg',
    content:
      "Finally, a task manager that doesn't feel like work to use. The elegant design and smooth animations make it a joy to check off my todos.",
    rating: 5,
  },
  {
    name: 'Priya Patel',
    role: 'Marketing Director',
    avatar: '/avatars/priya.jpg',
    content:
      "The AI chat feature understands exactly what I need. I can ask it to show me all urgent tasks for this week and it delivers instantly. Magic!",
    rating: 5,
  },
  {
    name: 'James Wilson',
    role: 'Consultant',
    avatar: '/avatars/james.jpg',
    content:
      "I've tried dozens of productivity apps over the years. This is the first one that actually stuck. The combination of features is unmatched.",
    rating: 5,
  },
];

export function TestimonialsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        cardsRef.current?.children || [],
        { opacity: 0, y: 30 },
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
    <section ref={sectionRef} className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Loved by <span className="text-gradient-gold">Thousands</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Join the community of productive people who have transformed their
            workflow with our app.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div
          ref={cardsRef}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {testimonials.map((testimonial) => (
            <Card
              key={testimonial.name}
              className="border-border/50 bg-card hover:shadow-lg transition-all duration-300"
            >
              <CardContent className="p-6">
                {/* Rating */}
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Star
                      key={i}
                      className="w-4 h-4 fill-primary text-primary"
                    />
                  ))}
                </div>

                {/* Content */}
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  &ldquo;{testimonial.content}&rdquo;
                </p>

                {/* Author */}
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10 border-2 border-primary/20">
                    <AvatarImage src={testimonial.avatar} alt={testimonial.name} />
                    <AvatarFallback className="bg-primary/10 text-primary font-medium">
                      {testimonial.name
                        .split(' ')
                        .map((n) => n[0])
                        .join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold text-sm">{testimonial.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
