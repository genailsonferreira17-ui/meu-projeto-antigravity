import { Composition } from "remotion";
import { Teste } from "./Teste";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Teste"
      component={Teste}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
