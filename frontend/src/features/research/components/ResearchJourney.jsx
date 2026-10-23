import { Check } from 'lucide-react';

export default function ResearchJourney({ stage }) {
  const current = stage === 'topic' ? 0 : stage === 'outline' ? 1 : 2;
  const steps = ['Choose a topic', 'Shape your research', 'Review & export'];
  return (
    <div className="journey" aria-label="Research steps">
      {steps.map((step, index) => (
        <div
          className={`journey-step ${index === current ? 'current' : index < current ? 'done' : ''}`}
          key={step}
        >
          <span>{index < current ? <Check size={13} /> : `0${index + 1}`}</span>
          {step}
          {index < 2 && <i />}
        </div>
      ))}
    </div>
  );
}
