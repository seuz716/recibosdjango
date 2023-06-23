from django.shortcuts import render, get_object_or_404, redirect
from .models import Recibo
from .forms import ReciboForm
from django.db import models



def home(request):
    recibo = Recibo.objects.first()  # Obtén el primer recibo (cambia esto según tu lógica)
    context = {'recibo': recibo}
    return render(request, 'recibos/home.html', context)


def recibo_list(request):
    codigo = request.GET.get('codigo', '')  # Obtén el parámetro de filtrado por código
    descripcion = request.GET.get('descripcion', '')  # Obtén el parámetro de filtrado por descripción

    recibos = Recibo.objects.all()
    
    # Aplica el filtrado si se proporcionan los parámetros
    if codigo:
        recibos = recibos.filter(codigo__icontains=codigo)
    if descripcion:
        recibos = recibos.filter(descripcion__icontains=descripcion)

    total_monto = recibos.aggregate(total_monto=models.Sum('monto'))['total_monto']

    context = {
        'recibos': recibos,
        'total_monto': total_monto,
        'codigo_filtro': codigo,
        'descripcion_filtro': descripcion
    }
    return render(request, 'recibos/recibo_list.html', context)


def recibo_detail(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    return render(request, 'recibos/recibo_detail.html', {'recibo': recibo})


def recibo_create(request):
    if request.method == 'POST':
        form = ReciboForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recibo_list')
    else:
        form = ReciboForm()
    return render(request, 'recibos/recibo_form.html', {'form': form})


def recibo_update(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)

    if request.method == 'POST':
        form = ReciboForm(request.POST, instance=recibo)
        if form.is_valid():
            form.save()
            return redirect('recibo_list')
    else:
        form = ReciboForm(instance=recibo)
    return render(request, 'recibos/recibo_form.html', {'form': form})


def recibo_delete(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)

    if request.method == 'POST':
        recibo.delete()
        return redirect('recibo_list')
    return render(request, 'recibos/recibo_confirm_delete.html', {'recibo': recibo})
