import { useEffect, type ReactNode } from "react";
import styles from "@/styles/Dictionary.module.css";

interface ModalProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
  /** 하단 버튼 영역 */
  footer?: ReactNode;
  wide?: boolean;
}

/**
 * 사전 화면 전용 모달 셸.
 * 별도 UI 라이브러리를 끌어오지 않고 기존 CSS 변수만으로 구성한다.
 */
export default function Modal({
  title,
  onClose,
  children,
  footer,
  wide,
}: ModalProps) {
  // ESC 로 닫기 + 배경 스크롤 잠금
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose]);

  return (
    <div
      className={styles.overlay}
      onMouseDown={(e) => {
        // 오버레이 자체를 눌렀을 때만 닫는다(내용 드래그 중 닫힘 방지).
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={`${styles.modal} ${wide ? styles.modalWide : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className={styles.modalHead}>
          <span className={styles.modalTitle}>{title}</span>
          <span className={styles.panelSpacer} />
          <button
            type="button"
            className={styles.iconBtn}
            onClick={onClose}
            aria-label="닫기"
            title="닫기"
          >
            ✕
          </button>
        </div>

        <div className={styles.modalBody}>{children}</div>

        {footer ? <div className={styles.modalFoot}>{footer}</div> : null}
      </div>
    </div>
  );
}
