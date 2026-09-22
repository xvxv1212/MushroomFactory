import manyangImg from "../../assets/마냥_기본.png";


interface ManyangCoachProps {
  feedback: string;
}


export default function ManyangCoach({
  feedback,
}: ManyangCoachProps) {

  return (
    <div className="manyang-coach">

      <div className="manyang-character">
        <img
          src={manyangImg}
          alt="마냥이"
        />
      </div>

      <div>
        <strong>마냥이</strong>

        <p>{feedback}</p>
      </div>

    </div>
  );
}
