// 條件跳題邏輯（根據 conditional_order 隱藏/顯示問題）
document.addEventListener('DOMContentLoaded', function() {
    const questions = document.querySelectorAll('.question');

    function rememberRequiredState(containerEl) {
        const inputs = containerEl.querySelectorAll('input, textarea, select');
        inputs.forEach(function(inp) {
            if (inp.required) {
                inp.dataset.wasRequired = '1';
            }
        });
    }

    function setQuestionEnabled(questionEl, enabled) {
        const inputs = questionEl.querySelectorAll('input, textarea, select');
        inputs.forEach(function(inp) {
            if (enabled) {
                inp.disabled = false;
                if (inp.dataset.wasRequired === '1') {
                    inp.required = true;
                }
            } else {
                if (inp.required) {
                    inp.dataset.wasRequired = '1';
                }
                inp.required = false;
                inp.disabled = true;
            }
        });
    }

    function clearQuestionAnswers(questionEl) {
        const inputs = questionEl.querySelectorAll('input, textarea, select');
        inputs.forEach(function(inp) {
            if (inp.type === 'radio' || inp.type === 'checkbox') {
                inp.checked = false;
            } else {
                inp.value = '';
            }
        });
    }

    // Cache original required state so we can restore it when showing questions.
    questions.forEach(function(q) {
        rememberRequiredState(q);
    });
    
    questions.forEach(function(questionEl) {
        const conditionalData = questionEl.dataset.conditional;
        if (!conditionalData) return;
        
        try {
            const conditional = JSON.parse(conditionalData);
            const inputs = questionEl.querySelectorAll('input[type="radio"]');
            
            if (inputs.length === 0) return;
            
            inputs.forEach(function(input) {
                input.addEventListener('change', function() {
                    const answer = this.value;
                    // 判斷是否為正向答案（YES, true, 1 等）
                    const isPositive = answer === 'YES' || answer === 'true' || answer === '1';
                    const nextOrder = isPositive 
                        ? conditional.positive_response_question_order 
                        : conditional.negative_response_question_order;
                    
                    const currentOrder = parseInt(questionEl.dataset.order);
                    
                    // 隱藏所有後續問題
                    questions.forEach(function(q) {
                        const order = parseInt(q.dataset.order);
                        if (order > currentOrder) {
                            q.classList.add('hidden');
                            // 隱藏的問題需要禁用，避免 required 造成表單無法送出
                            clearQuestionAnswers(q);
                            setQuestionEnabled(q, false);
                        }
                    });
                    
                    // 顯示對應的問題
                    if (nextOrder) {
                        questions.forEach(function(q) {
                            if (parseInt(q.dataset.order) === nextOrder) {
                                q.classList.remove('hidden');
                                setQuestionEnabled(q, true);
                            }
                        });
                    }
                });
            });
        } catch (e) {
            console.error('Error parsing conditional data:', e);
        }
    });
    
    // 初始化：隱藏所有有 conditional_order 的後續問題
    questions.forEach(function(questionEl, index) {
        const conditionalData = questionEl.dataset.conditional;
        if (conditionalData) {
            const currentOrder = parseInt(questionEl.dataset.order);
            // 隱藏所有 order > currentOrder 的問題
            questions.forEach(function(q) {
                const order = parseInt(q.dataset.order);
                if (order > currentOrder) {
                    q.classList.add('hidden');
                    setQuestionEnabled(q, false);
                }
            });
        }
    });
});
