

export const inputMessageInput = (message: string) => {
     
    // const editableDiv = document.querySelector('.msg-form__contenteditable');
    const editableDiv = document.querySelector('.artdeco-text-input--input');

    console.log(editableDiv);

    if (editableDiv) {
        editableDiv.innerHTML = message;
    }

}