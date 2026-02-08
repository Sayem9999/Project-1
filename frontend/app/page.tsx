import { Hero } from '@/components/ui/Hero';
import { FeatureGrid } from '@/components/ui/FeatureGrid';
import { HowItWorks } from '@/components/ui/HowItWorks';
import { Footer } from '@/components/ui/Footer';

export default function Home() {
  return (
    <>
      <Hero />
      <HowItWorks />
      <FeatureGrid />
      <Footer />
    </>
  );
}
