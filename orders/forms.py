from django import forms

STATES = [
    ("", "Selecione o estado"),
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins"),
]

PAYMENT_METHODS = [
    ("pix", "PIX"),
    ("credit_card", "Cartão de Crédito"),
    ("boleto", "Boleto"),
]

_INPUT = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
_SELECT = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"


class CheckoutForm(forms.Form):
    shipping_name = forms.CharField(
        label="Nome completo", max_length=150,
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": "Como está no documento"}),
    )
    shipping_cep = forms.CharField(
        label="CEP", max_length=9,
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": "00000-000"}),
    )
    shipping_street = forms.CharField(
        label="Rua e número", max_length=250,
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": "Rua das Flores, 123"}),
    )
    shipping_complement = forms.CharField(
        label="Complemento", max_length=100, required=False,
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": "Apto, bloco… (opcional)"}),
    )
    shipping_neighborhood = forms.CharField(
        label="Bairro", max_length=100,
        widget=forms.TextInput(attrs={"class": _INPUT}),
    )
    shipping_city = forms.CharField(
        label="Cidade", max_length=100,
        widget=forms.TextInput(attrs={"class": _INPUT}),
    )
    shipping_state = forms.ChoiceField(
        label="Estado", choices=STATES,
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    payment_method = forms.ChoiceField(
        label="Forma de pagamento", choices=PAYMENT_METHODS,
        widget=forms.RadioSelect,
        initial="pix",
    )

    def clean_shipping_cep(self):
        cep = self.cleaned_data.get("shipping_cep", "").replace("-", "").strip()
        if not cep.isdigit() or len(cep) != 8:
            raise forms.ValidationError("CEP inválido. Informe 8 dígitos numéricos.")
        return f"{cep[:5]}-{cep[5:]}"

    def clean_shipping_state(self):
        state = self.cleaned_data.get("shipping_state", "")
        if not state:
            raise forms.ValidationError("Selecione o estado.")
        return state

    def address_data(self):
        _FIELDS = frozenset([
            "shipping_name", "shipping_cep", "shipping_street", "shipping_complement",
            "shipping_neighborhood", "shipping_city", "shipping_state",
        ])
        return {k: v for k, v in self.cleaned_data.items() if k in _FIELDS}
