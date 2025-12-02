import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, CheckCircle2, Moon, Sun } from "lucide-react";
import { Link } from "react-router-dom";
import { GmailIcon, CalendarIcon, SlackIcon, MapsIcon, DiscordIcon, ChromeIcon } from "@/components/Icons";

export const LandingPage = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window !== 'undefined') {
      return (window.localStorage.getItem('retro-theme') as 'light' | 'dark') || 'light';
    }
    return 'light';
  });

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', theme === 'dark');
    }
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('retro-theme', theme);
    }
  }, [theme]);

  const toggleTheme = () => setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));

  return (
    <div className="min-h-screen bg-background flex flex-col font-retro text-foreground">
      {/* Header */}
      <header className="border-b-2 border-black bg-card p-4 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary border-2 border-black shadow-retro-sm"></div>
            <span className="font-bold text-xl uppercase tracking-tight">Champa</span>
          </div>
          <div className="flex gap-4 items-center">
            <Button
              variant="outline"
              size="icon"
              className="hidden sm:flex border-2 border-black shadow-retro-xs mr-2"
              onClick={toggleTheme}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </Button>
            <Link to="/login">
              <Button variant="outline" className="hidden sm:flex">Log In</Button>
            </Link>
            <Link to="/signup">
              <Button>Request Access</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-20 px-4 border-b-2 border-black bg-accent/10">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-block bg-secondary text-secondary-foreground px-4 py-1 border-2 border-black shadow-retro-sm font-bold text-sm uppercase tracking-wider mb-4">
              v0.1 Private Beta
            </div>
            <h1 className="text-4xl md:text-6xl font-bold leading-tight tracking-tighter uppercase">
              The Operating System <br />
              <span className="bg-primary text-primary-foreground px-2">For Your Social Life</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto font-sans">
              Streamline your daily workflow with a unified interface.
              Connect all your social platforms in one place without the distraction of modern clutter.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
              <Link to="/signup">
                <Button size="lg" className="w-full sm:w-auto text-lg px-8 h-14">
                  Join Waitlist <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-lg px-8 h-14 bg-background">
                View Demo
              </Button>
            </div>
          </div>
        </section>

        {/* Integrations Section */}
        <section className="py-20 px-4 bg-background">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16 space-y-4">
              <h2 className="text-3xl font-bold uppercase tracking-tight">Connected Intelligence</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                We've stripped away the noise and kept only what matters.
                Seamless integration with the tools you use every day.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {/* Gmail Card */}
              <Card className="bg-card hover:translate-y-[-4px] transition-transform duration-200">
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-red-100 border-2 border-black flex items-center justify-center shadow-retro-sm">
                    <GmailIcon className="w-6 h-6 text-red-600" />
                  </div>
                  <CardTitle>Gmail Integration</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Compose, read, and organize your emails directly from the command center.
                    Zero distractions, pure efficiency.
                  </p>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" /> Smart Filtering
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" /> Quick Actions
                    </li>
                  </ul>
                </CardContent>
              </Card>

              {/* Calendar Card */}
              <Card className="bg-card hover:translate-y-[-4px] transition-transform duration-200">
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-blue-100 border-2 border-black flex items-center justify-center shadow-retro-sm">
                    <CalendarIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <CardTitle>Calendar Sync</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Never miss a meeting. View your schedule in a brutalist, easy-to-read format.
                    One-click join for all calls.
                  </p>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" /> Auto-Scheduling
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" /> Time Blocking
                    </li>
                  </ul>
                </CardContent>
              </Card>

              {/* Slack Card */}
              <Card className="bg-card hover:translate-y-[-4px] transition-transform duration-200">
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-yellow-100 border-2 border-black flex items-center justify-center shadow-retro-sm">
                    <SlackIcon className="w-6 h-6 text-yellow-600" />
                  </div>
                  <CardTitle>Slack Connect</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Stay in the loop without the notification overload.
                    Prioritized messages delivered to your dashboard.
                  </p>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" /> Thread Summaries
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" /> Direct Replies
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>

            <div className="grid md:grid-cols-3 gap-8 mt-8">
              {/* Google Maps Card */}
              <Card className="bg-card/50 border-dashed hover:translate-y-[-4px] transition-transform duration-200 relative overflow-hidden">
                <div className="absolute top-3 right-3 bg-muted text-muted-foreground text-xs font-bold px-2 py-1 border border-black uppercase">
                  Coming Soon
                </div>
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-green-100 border-2 border-black flex items-center justify-center shadow-retro-sm grayscale">
                    <MapsIcon className="w-6 h-6 text-green-600" />
                  </div>
                  <CardTitle className="text-muted-foreground">Google Maps</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Navigate your world directly from your dashboard. Real-time traffic and location sharing.
                  </p>
                </CardContent>
              </Card>

              {/* Discord Card */}
              <Card className="bg-card/50 border-dashed hover:translate-y-[-4px] transition-transform duration-200 relative overflow-hidden">
                <div className="absolute top-3 right-3 bg-muted text-muted-foreground text-xs font-bold px-2 py-1 border border-black uppercase">
                  Coming Soon
                </div>
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-indigo-100 border-2 border-black flex items-center justify-center shadow-retro-sm grayscale">
                    <DiscordIcon className="w-6 h-6 text-indigo-600" />
                  </div>
                  <CardTitle className="text-muted-foreground">Discord</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Seamless voice and text chat integration. Stay connected with your communities.
                  </p>
                </CardContent>
              </Card>

              {/* Browser Card */}
              <Card className="bg-card/50 border-dashed hover:translate-y-[-4px] transition-transform duration-200 relative overflow-hidden">
                <div className="absolute top-3 right-3 bg-muted text-muted-foreground text-xs font-bold px-2 py-1 border border-black uppercase">
                  Coming Soon
                </div>
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-orange-100 border-2 border-black flex items-center justify-center shadow-retro-sm grayscale">
                    <ChromeIcon className="w-6 h-6 text-orange-600" />
                  </div>
                  <CardTitle className="text-muted-foreground">Web Browser</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    A built-in retro browser for distraction-free research and browsing.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Feature Strip */}
        <section className="py-12 border-y-2 border-black bg-primary text-primary-foreground overflow-hidden">
          <div className="flex gap-8 items-center justify-center font-bold text-2xl uppercase tracking-widest whitespace-nowrap animate-marquee">
            <span>• No Distractions</span>
            <span>• Pure Focus</span>
            <span>• Retro Style</span>
            <span>• Modern Power</span>
            <span>• No Distractions</span>
            <span>• Pure Focus</span>
            <span>• Retro Style</span>
            <span>• Modern Power</span>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-4 bg-card">
          <div className="max-w-3xl mx-auto text-center space-y-8 border-2 border-black p-8 shadow-retro bg-background">
            <h2 className="text-3xl font-bold uppercase">Ready to upgrade your workflow?</h2>
            <p className="text-muted-foreground">
              Join thousands of users who have reclaimed their productivity.
              Experience the future of work, designed like the past.
            </p>
            <div className="flex justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="w-full sm:w-auto">Request Access</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-black bg-muted py-12 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-primary border-2 border-black"></div>
            <span className="font-bold uppercase">Champa</span>
          </div>
          <div className="flex gap-8 text-sm font-bold uppercase text-muted-foreground">
            <a href="#" className="hover:text-foreground hover:underline">Privacy</a>
            <a href="#" className="hover:text-foreground hover:underline">Terms</a>
            <a href="#" className="hover:text-foreground hover:underline">Twitter</a>
            <a href="#" className="hover:text-foreground hover:underline">GitHub</a>
          </div>
          <div className="text-xs text-muted-foreground">© 2025 All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
};
